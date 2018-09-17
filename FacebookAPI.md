Facebook API Marketing Notes

### Facebook API Business Use and reports: 

- **Ad Reporting**: This enables you to see basic metrics for your ads such as impressions, clicks and conversions such as purchases and app installs
- **Order Level Reporting**: You can use these reports to understand which   ads led to a response at a specific point in a conversion funnel
- **Lift**: With Facebook Lift Measurement you can see the true impact your ads have on real people for any business objective, including direct response.
- **Audience Network**: With Audience Network, you can monetize your app by showing Facebook ads in it.
  - Facebook Audience Network is an off-Facebook, in-app advertising network for mobile apps. Advertisers can serve up their ads to customers who are using mobile sites and apps other than Facebook,  extending their reach beyond the platform while still getting to use Facebook’s exceptionally powerful ad system (see [here](<https://adespresso.com/blog/facebook-audience-network/>))
  - FAN audience placement ad options:
    - Native, banner, and interstitial
    - In-stream videos
    - Rewarded videos

![fb_Ad_placement](/Users/z013lgl/sandbox/github/seabull/resources/assets/fb_Ad_placement.png)

- **Attribution**: attribution is your ability to attribute a conversion to your ad. it represents causality
  between your ad and a response, such as a purchase. By gathering conversion events and proper attribution, you can see the path to conversion by constructing all the attribution points that lead up
  to a conversion. This is a great way to understand where and how to best invest on ads.

- **Signals**: The foundation for all measurement solutions is data input; the results you get are only as good as the data input into a solution. We call these data inputs **signals**.The Facebook tools you can use to get
  signals are *App Events*, *Facebook Pixel* and *offline conversions*.  

- **App Events**: To measure mobile app ad performance, you can either implement server-to-server calls or include the Facebook SDK and App Events in your   mobile app 

- **Facebook Pixel**: On desktop or mobile web, you use the **Facebook Pixel** to collect conversion data

- **Offline Conversions**: The **Offline conversions** API enables you to track and optimize for transactions that happen off your website or mobile app.This includes in stores, through call-centers, post payment methods, bank-transfers, and more. The Offline Conversion API is available only when you use Optimized Cost Per Mille bidding, known as oCPM, for your ads. 

- **Ads Pacing**: The goal of ads pacing is to evenly deliver ad impressions over a day.

- **Creative**: Ad creative defines all the assets and content which people see when your ad is shown. This includes images, text, and videos.

- The major types of ad formats for **direct response** on Facebook are **carousel**, **link**, and **video** ads.

- **Audience Matrices**: Segment audiences based on *how often* people engage with your business, *how recently* they engaged with your business and *by the lifetime value* of doing business with them. 

  - When you build **Custom Audiences** with Marketing API, Facebook can provide precise targeting for your ads to reach the user segment relevant to you. Some examples of targeting ads based on custom audiences include: 

    - Target ads at VIP users that have not returned in a while; provide   ad creative showing a reward when they return. 

    - Target people who left their shopping cart on your website or   app with a relevant image of the product they selected. 

- **Targeting Strategy**: In many cases you want to advertise to a segment of people with the value you attribute to reaching that audience. Since Facebook limits the number of times someone sees ads from the same page per day, you want your most relevant ads for a specific audience to have the highest chance of   winning at auction. This illustrates a tiered targeting strategy, which you can put into practice: 

  - First target the highest value user segment and bid their true value. For example, create an audience for store cardholders who already spend the most at your business. This is your most valuable segment and you should bid the most to reach them. 
  - Set the next segment, such as someone who made a single purchase, and bid lower than the top segment, and exclude the previous tier. 

- **Lookalike Audiences** are audiences modeled by Facebook to be similar to your given audience. see [here](http://fb.me/tieredla) 

- **Conversion Optimized Bidding**: Rather than bidding CPM or CPC, Conversion Optimized Bidding enables you to specify how  much a conversion event is worth to you. Facebook then calculates the value of an ad impression for each person during the ads auction based on their probability of the conversion   event occurring.

- Facebook uses **probabilistic modeling** to   calculate the value of your ad and whether  to show the ad to someone   

- **Optimize Conversion Funnels**: Facebook optimizes delivery of your ads against  one-day post-click conversion events

### Some useful URLs:

- [Marketing API SDKs](http://fb.me/sdks)
- [Sample Code Library](http://fb.me/samples)
- [Graph API Explorer](http://fb.me/explorer)
- [Access Token Debugger](http://fb.me/access)
- [Facebook Pixel Helper](http://fb.me/pixelhelp)
- [Webhook/Dynamic Ad debugger](http://fb.me/dadebug)
- [Dynamic Ads](http://fb.me/dynads)

