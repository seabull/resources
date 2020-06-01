Streaming (from Streaming Systems by Reuven Lax; Tyler Akidau; Slava Chernyak)



Streaming system: A type of data processing engine that is designed with infinite datasets in mind

Stream: An element-by-element view of the evolution of a dataset over time. The MapReduce lineage of data processing systems have traditionally dealt in streams

For those of you not already familiar with the **Lambda Architecture**, the basic idea is that you run a streaming system alongside a batch system, both performing essentially the same calculation. The streaming system gives you low-latency, inaccurate results (either because of the use of an approximation algorithm, or because the streaming system itself does not provide correctness), and some time later a batch system rolls along and provides you with correct output. Originally proposed by Twitter’s Nathan Marz (creator of [Storm](http://storm.apache.org/)), it ended up being quite successful because it was, in fact, a fantastic idea for the time; streaming engines were a bit of a letdown in the correctness department, and batch engines were as inherently unwieldy as you’d expect, so Lambda gave you a way to have your proverbial cake and eat it too. Unfortunately, **maintaining a Lambda system is a hassle: you need to build, provision, and maintain two independent versions of your pipeline and then also somehow merge the results from the two pipelines at the end.**

As someone who spent years working on a strongly consistent streaming engine, I also found the entire principle of the Lambda Architecture a bit unsavory. Unsurprisingly, I was a huge fan of Jay Kreps’ [“Questioning the Lambda Architecture”](https://oreil.ly/2LSEdqz) post when it came out. Here was one of the first highly visible statements against the necessity of dual-mode execution. Delightful. Kreps addressed the issue of repeatability in the context of using a replayable system like Kafka as the streaming interconnect, and went so far as to propose the **Kappa Architecture**, which basically means running a single pipeline using a well-designed system that’s appropriately built for the job at hand. I’m not convinced that notion requires its own Greek letter name, but I fully support the idea in principle.

Quite honestly, I’d take things a step further. I would argue that well-designed streaming systems actually provide a strict superset of batch functionality. Modulo perhaps an efficiency delta, there should be no need for batch systems as they exist today. And kudos to the [Apache Flink](http://flink.apache.org/) folks for taking this idea to heart and building a system that’s all-streaming-all-the-time under the covers, even in “batch” mode; I love it.

##### BATCH AND STREAMING EFFICIENCY DIFFERENCES

One which I propose is not an inherent limitation of streaming systems, but simply a consequence of design choices made in most streaming systems thus far. The efficiency delta between batch and streaming is largely the result of the increased bundling and more efficient shuffle transports found in batch systems. Modern batch systems go to great lengths to implement sophisticated optimizations that allow for remarkable levels of throughput using surprisingly modest compute resources. There’s no reason the types of clever insights that make batch systems the efficiency heavyweights they are today couldn’t be incorporated into a system designed for unbounded data, providing users flexible choice between what we typically consider to be high-latency, higher-efficiency “batch” processing and low-latency, lower-efficiency “streaming” processing. This is effectively what we’ve done at Google with Cloud Dataflow by providing both batch and streaming runners under the same unified model. In our case, we use separate runners because we happen to have two independently designed systems optimized for their specific use cases. Long term, from an engineering perspective, I’d love to see us merge the two into a single system that incorporates the best parts of both while still maintaining the flexibility of choosing an appropriate efficiency level. But that’s not what we have today. And honestly, thanks to the unified Dataflow Model, it’s not even strictly necessary; so it may well never happen.

only two things are necessary to take streaming systems beyond their batch counterparts: ***correctness*** and ***tools for reasoning about time***

Correctness

This gets you parity with batch. At the core, correctness boils down to consistent storage. Streaming systems need a method for checkpointing persistent state over time (something Kreps has talked about in his [“Why local state is a fundamental primitive in stream processing”](https://oreil.ly/2l8asqf) post), and it must be well designed enough to remain consistent in light of machine failures. When Spark Streaming first appeared in the public big data scene a few years ago, it was a beacon of consistency in an otherwise dark streaming world. Thankfully, things have improved substantially since then, but it is remarkable how many streaming systems still try to get by without strong consistency.

To reiterate—because this point is important: strong consistency is required for exactly-once processing,[3](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch01.html#idm45164589815272) which is required for correctness, which is a requirement for any system that’s going to have a chance at meeting or exceeding the capabilities of batch systems. Unless you just truly don’t care about your results, I implore you to shun any streaming system that doesn’t provide strongly consistent state. Batch systems don’t require you to verify ahead of time if they are capable of producing correct answers; don’t waste your time on streaming systems that can’t meet that same bar.

If you’re curious to learn more about what it takes to get strong consistency in a streaming system, I recommend you check out the [MillWheel](http://bit.ly/2Muob70), [Spark Streaming](http://bit.ly/2Mrq8Be), and [Flink snapshotting](http://bit.ly/2t4DGK0) papers. All three spend a significant amount of time discussing consistency. Reuven will dive into consistency guarantees in [Chapter 5](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch05.html#exactly_once_and_side_effects), and if you still find yourself craving more, there’s a large amount of quality information on this topic in the literature and elsewhere.

Event time

This is the time at which events actually occurred.

Processing time

This is the time at which events are observed in the system.

![Streaming_ProcssingEvent_time](/Users/z013lgl/sandbox/github/seabull/resources/Streaming_ProcssingEvent_time.png)

I propose that instead of attempting to groom unbounded data into finite batches of information that eventually become complete, we should be designing tools that allow us to live in the world of uncertainty imposed by these complex datasets. New data will arrive, old data might be retracted or updated, and any system we build should be able to cope with these facts on its own, with notions of completeness being a convenient optimization for specific and appropriate use cases rather than a semantic necessity across all of them.

# Data Processing Patterns

At this point, we have enough background established that we can begin looking at the core types of usage patterns common across bounded and unbounded data processing today. We look at both types of processing and, where relevant, within the context of the two main types of engines we care about (batch and streaming, where in this context, I’m essentially lumping microbatch in with streaming because the differences between the two aren’t terribly important at this level).

## Bounded Data

Processing bounded data is conceptually quite straightforward, and likely familiar to everyone. In [Figure 1-2](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch01.html#bounded_data_processing_with_a_classic_batch_engine), we start out on the left with a dataset full of entropy. We run it through some data processing engine (typically batch, though a well-designed streaming engine would work just as well), such as [MapReduce](http://bit.ly/2sZNfuA), and on the right side end up with a new structured dataset with greater inherent value.

## Unbounded Data: Batch

Batch engines, though not explicitly designed with unbounded data in mind, have nevertheless been used to process unbounded datasets since batch systems were first conceived. As you might expect, such approaches revolve around slicing up the unbounded data into a collection of bounded datasets appropriate for batch processing.

### FIXED WINDOWS

The most common way to process an unbounded dataset using repeated runs of a batch engine is by windowing the input data into fixed-size windows and then processing each of those windows as a separate, bounded data source (sometimes also called *tumbling windows*), as in [Figure 1-3](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch01.html#unbounded_data_processing_via_ad_hoc_fixed_windows_with_a_classic_batch_engine). Particularly for input sources like logs, for which events can be written into directory and file hierarchies whose names encode the window they correspond to, this sort of thing appears quite straightforward at first blush because you’ve essentially performed the time-based shuffle to get data into the appropriate event-time windows ahead of time.

### SESSIONS

This approach breaks down even more when you try to use a batch engine to process unbounded data into more sophisticated windowing strategies, like sessions. Sessions are typically defined as periods of activity (e.g., for a specific user) terminated by a gap of inactivity. When calculating sessions using a typical batch engine, you often end up with sessions that are split across batches, as indicated by the red marks in [Figure 1-4](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch01.html#unbounded_data_processing_processing_into_sessions_via_ad_hoc_fixed). We can reduce the number of splits by increasing batch sizes, but at the cost of increased latency. Another option is to add additional logic to stitch up sessions from previous runs, but at the cost of further complexity.Either way, using a classic batch engine to calculate sessions is less than ideal. A nicer way would be to build up sessions in a streaming manner, which we look at later on.

## Unbounded Data: Streaming

Contrary to the ad hoc nature of most batch-based unbounded data processing approaches, streaming systems are built for unbounded data. As we talked about earlier, for many real-world, distributed input sources, you not only find yourself dealing with unbounded data, but also data such as the following:

- Highly unordered with respect to event times, meaning that you need some sort of time-based shuffle in your pipeline if you want to analyze the data in the context in which they occurred.
- Of varying event-time skew, meaning that you can’t just assume you’ll always see most of the data for a given event time *X* within some constant epsilon of time *Y*.

There are a handful of approaches that you can take when dealing with data that have these characteristics. I generally categorize these approaches into four groups: **time-agnostic, approximation, windowing by processing time, and windowing by event time.**

Time-agnostic: e.g. filtering, inner join, 

**Windowing** is simply the notion of taking a data source (either unbounded or bounded), and chopping it up along temporal boundaries into finite chunks for processing. (e.g. Fixed windows, Sliding, Sessions)

one very big downside to **processing-time windowing**: *if the data in question have event times associated with them, those data must arrive in event-time order if the processing-time windows are to reflect the reality of when those events actually happened.*

powerful semantics rarely come for free, and event-time windows are no exception. Event-time windows have two notable drawbacks due to the fact that windows must often live longer (in processing time) than the actual length of the window itself: Buffering and Completeness

*Time (event_time), Windowing(fixed, sliding, sessions), Triggers, Watermarks, Accumulation*

*Triggers*: A trigger is a mechanism for declaring when the output for a window should be materialized relative to some external signal. e.g. *Repeated update triggers* (aligned delays, unaligned delays), *Completeness triggers*

*Watermarks*: A watermark is a notion of input **completeness** with respect to event times. A watermark with value of time *X* makes the statement: “all input data with event times less than *X* have been observed.” It is essentially a function of *F*(*P*) → *E* where P is processing time and E is event time. e.g. *Perfect watermarks*, *Heuristic watermarks*

*Accumulation*: An accumulation mode specifies the relationship between multiple results that are observed for the same window. e.g. *Discarding*, *Accumulating*, *Accumulating and retracting*

- *What* results are calculated? This question is answered by the types of transformations within the pipeline. This includes things like computing sums, building histograms, training machine learning models, and so on. It’s also essentially the question answered by classic batch processing
- *Where* in event time are results calculated? This question is answered by the use of event-time windowing within the pipeline. This includes the common examples of windowing from [Chapter 1](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/ch01.html#streaming_one_oh_one) (fixed, sliding, and sessions); use cases that seem to have no notion of windowing (e.g., time-agnostic processing; classic batch processing also generally falls into this category); and other, more complex types of windowing, such as time-limited auctions. Also note that it can include processing-time windowing, as well, if you assign ingress times as event times for records as they arrive at the system.
- *When* in processing time are results materialized? This question is answered by the use of triggers and (optionally) watermarks. There are infinite variations on this theme, but the most common patterns are those involving repeated updates (i.e., materialized view semantics), those that utilize a watermark to provide a single output per window only after the corresponding input is believed to be complete (i.e., classic batch processing semantics applied on a per-window basis), or some combination of the two.
- *How* do refinements of results relate? This question is answered by the type of accumulation used: discarding (in which results are all independent and distinct), accumulating (in which later results build upon prior ones), or accumulating and retracting (in which both the accumulating value plus a retraction for the previously triggered value(s) are emitted).

**You simply cannot get both low latency and correctness out of a system that relies solely on notions of completeness**. If repeated update triggers provide low-latency updates but no way to reason about completeness, and watermarks provide a notion of completeness but variable and possible high latency, why not combine their powers together?

``` Java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
               .triggering(AfterWatermark()
			     .withEarlyFirings(AlignedDelay(ONE_MINUTE))
			     .withLateFirings(AfterCount(1))))
  .apply(Sum.integersPerKey());
```

The biggest remaining difference between the perfect and heuristic early/on-time/late versions at this point is window lifetime bounds. In the perfect watermark case, we know we’ll never see any more data for a window after the watermark has passed the end of it, hence we can drop all of our state for the window at that time. In the heuristic watermark case, we still need to hold on to the state for a window for some amount of time to account for late data. But as of yet, our system doesn’t have any good way of knowing just how long state needs to be kept around for each window. That’s where ***allowed lateness*** comes in.

As a result, any real-world out-of-order processing system needs to provide some way to bound the lifetimes of the windows it’s processing. A clean and concise way of doing this is by defining a horizon on the allowed lateness within the system; that is, placing a bound on how late any given *record* may be (relative to the watermark) for the system to bother processing it; any data that arrives after this horizon are simply dropped.

##### MEASURING LATENESS

It might seem a little odd to be specifying a horizon for handling late data using the very metric that resulted in the late data in the first place (i.e., the heuristic watermark). And in some sense it is. But of the options available, it’s arguably the best. The only other practical option would be to specify the horizon in processing time (e.g., keep windows around for 10 minutes of processing time after the watermark passes the end of the window), but using processing time would leave the garbage collection policy vulnerable to issues within the pipeline itself (e.g., workers crashing, causing the pipeline to stall for a few minutes), which could lead to windows that didn’t actually have a chance to handle late data that they otherwise should have. By specifying the horizon in the event-time domain, garbage collection is directly tied to the actual progress of the pipeline, which decreases the likelihood that a window will miss its opportunity to handle late data appropriately.

Note however, that not all watermarks are created equal. When we speak of watermarks in this book, we generally refer to *low* watermarks, which pessimistically attempt to capture the event time of the *oldest* unprocessed record the system is aware of. The nice thing about dealing with lateness via low watermarks is that they are resilient to changes in event-time skew; no matter how large the skew in a pipeline may grow, the low watermark will always track the oldest outstanding event known to the system, providing the best guarantee of correctness possible.

``` Java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
               .triggering(
                 AfterWatermark()
                   .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                   .withLateFirings(AfterCount(1))
               .withAllowedLateness(ONE_MINUTE))
 .apply(Sum.integersPerKey());
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
               .triggering(
                 AfterWatermark()
                   .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                   .withLateFirings(AtCount(1))
               .discardingFiredPanes())
  .apply(Sum.integersPerKey());
```



In contrast, some systems may use the term “watermark” to mean other things. For example, [watermarks in Spark Structured Streaming](http://bit.ly/2yhCHMm) are *high* watermarks, which optimistically track the event time of the *newest* record the system is aware of. When dealing with lateness, the system is free to garbage collect any window older than the high watermark adjusted by some user-specified lateness threshold. In other words, the system allows you to specify the maximum amount of event-time skew you expect to see in your pipeline, and then throws away any data outside of that skew window. This can work well if skew within your pipeline remains within some constant delta, but is more prone to incorrectly discarding data than low watermarking schemes.