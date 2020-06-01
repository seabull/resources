# Is Shapeless worth it? What is Shapeless anyway?

This article explores what generic programming is, how it can be used to solve the problem of reusing the same Spark code as concrete types change through your pipeline, and why [Shapeless](https://github.com/milessabin/shapeless/wiki/Feature-overview:-shapeless-2.0.0) is largely the tool of choice for generic programming in Scala. I also present some style suggestions for working with Shapeless.

It’s worth noting that if you really want to go down this path in Spark code, the [Frameless](https://github.com/typelevel/frameless) project aims to facilitate that.

**TL;DR:** Yeah, Shapeless is kinda worth it. None of the alternatives are better. It gives you type safety where other techniques would not provide it, but it requirements a fair investment of time to learn how to write it. It’s easy to write it in a way that is easy to read even for people who don’t know it.

## What is generic programming and how does Shapeless fit in?

Generic programming does not have a singular definition I can find, but synthesising [these](https://en.wikipedia.org/wiki/Generic_programming) [sources](http://www.cs.ox.ac.uk/jeremy.gibbons/publications/scalagp-jfp.pdf), I would define it as writing programs for types to be specified later, where there is no meaningful base class onto which to stuff all the operations. To quote from the [linked paper](http://www.cs.ox.ac.uk/jeremy.gibbons/publications/scalagp-jfp.pdf):

> parametric polymorphism abstracts from the ‘integers’ in ‘lists of integers’, whereas [generic programming] abstracts from the ‘lists of’

In fact, our example will focus on “the integers” where “the integers” are in fact case classes.

Shapeless fits in as the premier Scala library for generic programming. Its big advantage is that it doesn’t lose type safety, and in effect provides a type-based mini language for programming the compiler. In short, it’s the pre-written, compiler-checked option in this space in Scala.

## Why would I want to do generic programming?

Any time the alternatives are copypasta or jamming something awkwardly on a remote base class, generic programming starts to look very good.

In general, in any case where you want to make sure exactly the same logic is used for multiple types, you have a good case for generic programming.

## Show me a problem being solved with generic programming right now

Consider the following problem: We want to bring together data about when certain set top boxes are tuned to certain channels (viewership), join it with information about what was playing on those channels (schedules), and roll it up into time segments (for ease of querying) based on the viewership and schedule characteristics. Later, the schedule information changes, and so we need to compute refreshed final data. Ignoring the option of storing our intermediates (data size and master data management issues make this relatively unattractive unless the necessary infrastructure is in place), the next option is to rematch the schedule data against the final data.

One solution is to use a dynamically typed solution (Python generally, or DataFrames in any Spark-supported language). This option allows us to write uncluttered code, and is an excellent solution in many cases. Indeed, the ability to write generic code without any particular ceremony is a huge reason to use dynamic languages. The disadvantage of this style of programming is that there is no automated, compile-time check that the data being passed in conforms to the schema that the code assumes it has. In data-heavy work, this can make code much more difficult to change, as commonly implicit assumptions about the shape of the data are scattered through the code. (As an aside: any generally applicable suggestions for solving that problem are welcome). Reflection-based approaches suffer from the same lack of type-checking, although they may be easier to test.

One solution to solving the schema-assumption problem is to make the schema explicit, and tag the code with the types involved. With concrete types it looks like this:

```scala
case class Viewership(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp, viewership_property: String)

case class Schedule(
  program_id: Integer, date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp)

case class ViewershipWithSchedule(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp,
  viewership_property: String, program_id: Integer)

def matchViewershipWithSchedules(
  viewership: Dataset[Viewership], schedules: Dataset[Schedule]): Dataset[ViewershipWithSchedule] = {
  import session.implicits._

  viewershipWithQHAndDate.toDF.as('viewership).join(schedules.toDF.as('schedules),
    $"viewership.date" === $"schedules.date"
      && $"viewership.segment_time" === $"schedules.segment_time"
      && $"viewership.station_id" === $"schedules.station_id")
    // filter on start and end time to avoid spurious matches
    .filter(
      $"schedules.start_time" < $"viewership.end_time")
        && $"schedules.end_time" > $"viewership.start_time")
    )
    .selectExpr("viewership.*", "schedules.program_id").as[ViewershipWithSchedule]
}
```



Very good so far — we have made the schemas explicit, put them in our parameter list, and the compiler will check them for us.

**A Parametric Solution:** If we don’t want to return to DataFrames, our options are to copy and paste with different type signatures, or abstract over the types of the case classes. Here is a preliminary version:

```scala
def matchViewershipWithSchedules[T, RESULT](
  viewership: Dataset[T], schedules: Dataset[Schedule])(
  // You need this so that RESULT can be used as a type parameter
  // inside the body of the function. A quirk of how Scala conforms
  // to Java's type erasure rules
  implicit ev: TypeTag[RESULT]): Dataset[RESULT] = {
  import session.implicits._

  viewershipWithQHAndDate.toDF.as('viewership).join(schedules.toDF.as('schedules),
    $"viewership.date" === $"schedules.date"
      && $"viewership.segment_time" === $"schedules.segment_time"
      && $"viewership.station_id" === $"schedules.station_id")
    // filter on start and end time to avoid spurious matches
    .filter(
      $"schedules.start_time" < $"viewership.end_time")
        && $"schedules.end_time" > $"viewership.start_time")
    )
    .selectExpr("viewership.*", "schedules.program_id").as[RESULT]
}
```



Looks typesafe, but isn’t

This should compile just fine. Unfortunately, we now have no guarantee that this will actually work at runtime, because we don’t know what’s in `viewership` any more — it could be anything.

**A Generic Solution**: So, we want to specify that `viewership` has the time columns we expect. We also still want to bring through all the columns that were on viewership, but now we have to handle that there will be clashes between the column names on our final data (it will have `program_id`) and the schedules data.

Let’s tackle the type constraints first:

```scala
trait TimeColumns {
  val date: Date
  val segment_time: Timestamp
  val station_id: Integer
  val start_time: Timestamp
  val end_time: Timestamp
}

case class Viewership(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp, 
  viewership_property: String) with TimeColumns

case class Schedule(
  program_id: Integer, 
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp) with TimeColumns

case class ViewershipWithSchedule(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp,
  viewership_property: String, program_id: Integer) with TimeColumns

def matchViewershipWithSchedules[T <: TimeColumns, RESULT](
  viewership: Dataset[T], schedules: Dataset[Schedule])(
  // You need this so that RESULT can be used as a type parameter
  // inside the body of the function. A quirk of how Scala conforms
  // to Java's type erasure rules
  implicit ev: TypeTag[RESULT]): Dataset[RESULT] = {
  import session.implicits._

  viewershipWithQHAndDate.toDF.as('viewership).join(schedules.toDF.as('schedules),
    $"viewership.date" === $"schedules.date"
      && $"viewership.segment_time" === $"schedules.segment_time"
      && $"viewership.station_id" === $"schedules.station_id")
    // filter on start and end time to avoid spurious matches
    .filter(
      $"schedules.start_time" < $"viewership.end_time")
        && $"schedules.end_time" > $"viewership.start_time")
    )
    // DANGER! if you pass in a ViewershipWithSchedule as the viewership, this will break
    .selectExpr("viewership.*", "schedules.program_id").as[RESULT]  // Line 39
}
```



Looks good so far. Now let’s tackle filling out the columns to select at line 39. Being as we’re using Spark, we could probably recover the column names from the DataSet objects. That’s not a bad solution, but we put our schema information in the case classes, not the DataSets. While I can’t think of a concrete problem with that, we’re inviting some kind of lost in translation problem, so let’s avoid it.

Take a deep breath: this is going to be a big change.

```scala
import shapeless._
import ops.record._
import ops.hlist._

trait TimeColumns {
  val date: Date
  val segment_time: Timestamp
  val station_id: Integer
  val start_time: Timestamp
  val end_time: Timestamp
}

case class Viewership(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp, 
  viewership_property: String) with TimeColumns

case class Schedule(
  program_id: Integer, 
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp) with TimeColumns

case class ViewershipWithSchedule(
  date: Date, segment_time: Timestamp, station_id: Integer, start_time: Timestamp, end_time: Timestamp,
  viewership_property: String, program_id: Integer) with TimeColumns

  // This is in a class so that we can specify the type RESULT explicitly without explicitly
  // specifying the type parameters to matchViewershipWithSchedules - we want the compiler
  // to calculate those types for us and "conjure" the objects using implicit resolution
  class ViewershipMatcher[RESULT <: Product] {
    // Holy Type Noise!
    // This stuff has to be captured at the boundary of concrete type land and generic type land
    // going deeper, this information won't be available to the compiler unless captured here
    // At this point the compiler is doing computations for us
    def matchViewershipWithSchedules[
      VQH <: TimeColumns with Product, ReprVQH <: HList, KeyVQHOut <: HList,
      ReprSchedule <: HList, KeyScheduleOut <: HList
    ](
      viewershipWithQHAndDate: Dataset[VQH], schedules: Dataset[Schedule])(
      implicit
        // Be case classes
        ev0: R <:< Product,
        ev1: VQH <:< Product,
        // Necessary if trying to pass down to any generic functions
        ev2: TypeTag[RESULT],
        ev3: TypeTag[VQH],
        // Have compiler retrieve the parameters to the case classes
        ev4: LabelledGeneric.Aux[VQH, ReprVQH],
        ev5: LabelledGeneric.Aux[Schedule, ReprSchedule],
        // we want these keys
        keysVQH: Keys.Aux[ReprVQH, KeyVQHOut],
        keysSchedule: Keys.Aux[ReprSchedule, KeyScheduleOut],
        // and we want to convert them to a list of Symbols
        traversableVQH: ToTraversable.Aux[KeyVQHOut, List, scala.Symbol],
        traversableSchedule: ToTraversable.Aux[KeyScheduleOut, List, scala.Symbol]
    ): Dataset[RESULT] = {
      import session.implicits._

      val viewershipJoinWithSchedules = viewershipWithQHAndDate.toDF.as('viewership).join(schedules.toDF.as('schedules),
        $"viewership.date" === $"schedules.date"
          && $"viewership.segment_time" === $"schedules.segment_time"
          && $"viewership.station_id" === $"schedules.station_id")
        // filter on start and end time to avoid spurious matches
        .filter(
          $"schedules.start_time" < $"viewership.end_time")
            && $"schedules.end_time" > $"viewership.start_time")
      )
      
      // Calculate the columns to select without ambiguity
      val schedulesProps = Set[String](keysSchedule.apply.toList.map(_.name):_*)
      val viewershipProps =
        Set[String](keysVQH.apply.toList.map(_.name):_*) -- schedulesProps
      // Select everything in viewership unless defined in schedules (i.e. schedules should override)
      val finalSelects: Seq[String] =
        (viewershipProps.map(x=>s"viewership.${x}") ++ schedulesProps.map(x=>s"schedules.${x}")).toSeq
      
      viewershipJoinWithSchedules
      // filter spurious matches
      // Sharp-eyed readers will note that running data repeatedly through this filter runs the risk of losing data
      // Consider that a problem for another time.
        .filter(
          unix_timestamp($"schedules.program_utc_start_time") < unix_timestamp($"viewership.tuning_utc_end_time")
            && unix_timestamp($"schedules.program_utc_end_time")   > unix_timestamp($"viewership.tuning_utc_start_time")
        )
        .selectExpr(finalSelects:_*).as[RESULT]
    }
  }
```



A working, (mostly) typesafe example

Hopefully this is fairly easy to read. We have added some not insignificant boilerplate, but we have very clearly described to the reader and the compiler the requirements we place on our input data, and we have avoided writing any reflection-based code ourselves to retrieve the keys.

Incidentally, the one piece of safety we are missing here is that we don’t automatically check that the result type is conformable with the selected columns from the input types. For that, we would need to move the column merge into the type parameters, and compare with the fields in RESULT. With that change, this code would be bulletproof.

Writing this code was harder than reading it — there isn’t great step-by-step documentation for Shapeless, and frequently I had to refer to the code to find out how it all fit together. A lot of the time the compiler generates helpful error messages, but sometime the error messages took me on a wild goose chase. [Indeed, this StackOverflow post was instrumental in getting this code to work.](https://stackoverflow.com/questions/46525541/how-to-generically-extract-field-names-with-shapeless)

That said, I could probably have read this [book length guide to Shapeless](https://github.com/underscoreio/shapeless-guide)and picked up a lot that way; indeed I probably will read it.

## Was it worth it? Would I do it again?

On the whole, I think I will do this kind of thing again. Learning to work with Shapeless will be effort amortized over using it. I really hate it when my ETLs die in production, and I hate chasing down data shape issues.

Library writers make some [wonderful generic interfaces](https://github.com/milessabin/shapeless/wiki/Built-with-shapeless) which require no boilerplate on the part of the library user. A[ list of some of them are here.](https://github.com/milessabin/shapeless/wiki/Built-with-shapeless)The more boilerplate you’re generating in your own code, the more I would recommend looking at Shapeless.

## Let’s talk about style

[The Type Astronaut’s Guide to Shapeless](https://github.com/underscoreio/shapeless-guide) has a whole chapter dedicated to style, and I have also relied on the [guidance given here.](https://gitter.im/milessabin/shapeless?at=5a480133edd2230811f512ca)

Look at the code above again, and hopefully you will notice a few things:

- Descriptive names of implicit parameters that are of any interest later in the code
- Types we want to specify explicitly MUST be in a different type parameter list from types we want calculated by the compiler
- Comments explain what the implicits are, because they are code
- Implicit parameters should be laid out in logical order leading up to what we want
- Unfortunately, because implicit resolution happens in textual order, we had to put the `ToTraversable` instances at the end
- You need to put all this implicit magic at the entry point to generic code — the TypeTags help make the types so tagged (i.e. the `T` in `TypeTag[T]`) available in the body of the function, but because types are erased by the compiler in conformity with Java’s erasure rules, the compiler cannot fully infer the necessary implicits on further nested calls.

## Conclusion

See the TL;DR at the top of the article, but in short if you like type safety and you don’t like copypasta, it’s a strong option. Your other options will likely involve a zone of non-safety and testing around that.

*If you learned from this article, please hit the “Clap” button. Claps help bring this article to the attention of more readers in the Medium network.*

[Build and Learn](https://medium.com/build-and-learn?source=post_sidebar--------------------------post_sidebar-)