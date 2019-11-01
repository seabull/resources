## REST API Types

REST designs fall under 3 different types:

- **Normal collection of resources** - tend to be full CRUD (POST, GET, PUT, DELETE). For example: /cars/v1, /dogs/v1, /products/v4, etc.
- **Transaction resource**- meant for transaction events or remote procedures that need to be triggered. Example would be an API to send an email to someone (POST /emails/v1/). Tend to not have GET, PUT, or DELETE needs (but can have GET if you need to look up a transaction).
- **Search** - for searching across 1 or multiple collection of resources where the attributes you’re searching for are not attributes in the resource of the collection of resources itself (e.g. search_phrase, lat, long, etc) OR where you’re searching for things across multiple collections of resources (e.g. search across cars, cats, dogs - all different collections) - in most cases you don’t need a search resource in your API (e.g. cars/v1/search); instead you can probably just whittle down the list of resources by passing in query parameters that already attributes in the model of the resources (e.g. cars/v1?color=red&make=ford).

### Normal Collection of Resources

Typically you have 5 actions you need to do with a collection of resources:

- List the existing resources in a collection (e.g. GET /cars/v1)
- Create a new resource (e.g. POST /cars/v1)
- Read an existing resource (e.g. GET /cars/v1/{car_id})
- Update an existing resource (e.g. PUT /cars/v1/{car_id})
- Delete an existing resource (e.g. DELETE /cars/v1/{car_id})

For limiting a list, use query params from attributes that exist in the data model of the resource (e.g. GET /cars/v1/?color=red,orange&year=2010) AND use limit and offset query params to page the results.

### Transaction

- Always use a POST to create your resource
- Be sure that the resource you just created with your POST has an ID. It may feel like you don’t need one, but all things created should have an ID AND you want to future proof yourself in case you ever want to do a GET to lookup a transaction (assumes you would of course store it in a DB). To do this, a recommendation is to use a UUID v4 for your ID of the resource (e.g. POST /emails/v1/ would have a response attribute in the JSON body of `"email_id": 72caf130-1801-4624-b8ff-71f7ea106d5c,`
- You typically won’t have a need to GET, PUT, or DELETE these transactions given the nature of the transaction may not allow you to do some of them, but it’s possible and you can if you want to.

### Search

Search is mostly different because of how the query params work:

- Use GET for the search (not POST); forces the search to be all query params (good for logging too)
- The q= param can be used for the search term that will be used to search across whatever attributes of the resources you document that it will search across. (e.g. GET /cars/v1/search?q=awesome which might search across description, owner_name, make, model)
- For attributes that are in the resource that you’re searching against, make sure they’re named the same (e.g. the “make” attribute in the JSON body of a car should also be “make” in the query parameter)
- Any attribute that you’re searching with that isn’t an attribute in the resource can be whatever you want to name it; just document the name and what it is in your Swagger spec so it ends up in API documentation
- Strongly consider paging your results (see below on how to do that; it involves Link headers for first, last, next, and previous AND page and per_page query params)
- Encase your results in an array with information following this example (it’s what GitHub API v3 does):

### General API Design

- **Do** use pragmatic REST design, not dogmatic REST design; design the API to maximize developer productivity and success as the primary design principle.

- **Do** Keep simple things simple. ** Ideally a developer doesn’t need to grok how the API behaves. They can experiment with and learn the API without having to dig into the documentation.

- Do use the appropriate HTTP response codes.

  <http://en.wikipedia.org/wiki/HTTP_response_codes>

  - 2xx codes for successful requests. Doesn’t necessarily mean a complete response, just that the request was received, understood and accepted.
  - 3xx codes for redirection. The client (caller) needs to take additional action to complete the request.
  - 4xx codes for client errors. The server believes the client has made a mistake. E.g. incorrectly formatted requests (400) or requested resource not found (404).
  - 5xx codes for server errors. The server understood the request but encountered an error trying to fulfill it.

- **Do** use caching headers whenever you can.

- **Do** everything you can to honor caching headers in a request.

- **Do** use redirects when they make sense, but these should be rare.

- **Do** made attribute names the same across query parameters, request body, and response body (e.g. in a JSON request and response don’t do this for the object item name: expiry, expiry_date and expirydate. Just make it expiry_date)

- **Don’t** put metadata in the body of a response that should go in the header.

- **Don’t** use underscore(*) in headers. Use ‘-’ instead of ‘*’ where multiword headers to be added.

- **Don’t** put metadata in a separate resource unless including it creates significant overhead.

- **Don’t** try to get hostname from URI if your api is java based API as all java API methods don’t like `_` in hostname and so you might get validation error as hostname is altered and added with underscores as part of standard ES template.. There are actually various other java API methods like `HttpServletRequest.getRequestURI` if you really need to use hostname from URI. There is an option of getting hostname from HOST header if you really need it.

### URIs

URIs should be [opaque](http://www.w3.org/DesignIssues/Axioms.html#opaque), but that doesn’t mean they need to be unreadable. The following tips can help you create easy-to-read URIs:

- **Do** use nouns in your URLs; in your URLs nouns are good; verbs are bad (your verbs should be HTTP verbs: POST, GET, PUT, and DELETE).
- **Do** use plural nouns; singular nouns don’t read as intuitively as plural.
- **Do** use concrete names (products, locations, ship_restrictions, etc); they are more meaningful than abstract names (item, entry, etc.).
- **Do** limit your URI space as much as possible.
- **Do** trail with no slash (e.g. do products/v3, not products/v3/
- **Do** use query parameters for sub-selection of a resource; i.e. pagination, queries, key validation, partial response with field_groups, page, per_page, etc.
- **Do**’ use path elements to identify resources rather than query parameters. For example, /resource/{id} instead of /resource?id={id}.
- **Do** move stuff out of the URI that should be in an HTTP header (HATEOS link pagination, basic auth headers, etc.)
- **Do** use lowercase snake_case paths, parameters, etc; e.g. this /this_is_a_long_name/ instead of /thisIsALongName/.
- **Don’t** use implementation-specific extensions in your URIs (.php, .py, .pl, etc.).
- **Don’t** fall into RPC with your URIs (e.g. don’t do /create_car/v1; instead do POST on /cars/v1)

### HTTP Methods

- Do use HTTP verbs to operate on the collections and elements.
  - HTTP verbs are POST, GET, PUT, and DELETE (think of them as mapping to the old metaphor of CRUD (Create-Read-Update-Delete)).
- **Do** use GET for as much as possible. GET calls should always be safe.
- **Do** use DELETE to remove resources.
- **Do** use POST for things like calculations (it’s a transactional endpoint)
- **Don’t** ever use GET to alter state. GET calls should always be safe.
- **Do** use PUT to update an entire resource or partially update a resource (we don’t use PATCH).
- **Don’t** use PUT unless you can also legitimately do a GET on the same URI.

### Resource Modeling

A resource can be thought of as a collection of things (dogs, cars, products, etc); in fact, you call it a “collection of resources”. A resource will have a canonical model (a car has a has a canonical model of attributes that makes up what a car is). It’s important to understand this concept, because this forms the foundation for how you model a RESTful API.

An API can be made up of 1 or more resources. For example:

- 1 resource API: just /cars/v1/ (list cars, look up individual cars, etc)
- 2 separate resources, but nested: /cars/v1 and /cars/v1/:car_id/owners/ (list owners for a car, look up a specific owner of car, etc)

Sometimes you have sub resources in an API. For example: separate resources under 1 API: /cars/v1/ AND /cars/categories (list categories, look up the details of an individual category, etc). Yes, a category about car categories is closely related to a realm/idea of cars, so that’s why it’s contained within the cars API, but a category is an entirely different resource with it’s own canonical model than a car itself (that’s a strong sign it should be its own resource), so that’s why it’s its own resource.

In these 3 examples, “cars”, “owners”, and “categories” are all separate resources.

#### Benefits

When you take the time to model your APIs in proper RESTful resources, then you’re probably solving the problem you had in the past where custom integrations were made all over the place for each consumer of data that came along. This planful approach stops that and does its best to layout resources for any type of consumer who comes along and needs reasonable, well modeled, explained, and easy to understand access to data in an API.

#### Caution with Orchestrated Combined Resources

It may be tempting to orchestrate several API calls into a new single resource (often times in the name of performance). The pitfalls:

- You’re setting the precedent that you’re okay with creating custom resources for each consumer that comes along and asks for them; you risk undoing the benefits (see above) and going back to the way things were with custom built integrations for each consumer that comes along)
- These custom orchestrated resources can’t be RESTful (see above, they have no canonical model which is a red flag it isn’t a true RESTful resource – when you begin to define it, you’ll notice the struggle right away when trying to come up with the right plural noun for such a resource – that too is a red flag)
- If you allow it, then you have to test it (duplicate work that is unnecessary), version it in new major versions, monitor it (take 2 am calls for the one-off thing that few consumers use), maintain it (take enhancement request for it), document it (explain the nuances of why it exists when people get confused at the RESTful deviation)

Remember, like Twitter, Facebook, GitHub, or any successful API in the real world, keep your API resource as resources. Don’t try to orchestrate them. Leave it to the clients; they are best situated to benefit from all the clean resources a well thought out API has to offer.

### Formats

Use [Snake Case](http://en.wikipedia.org/wiki/Snake_case) formatting. Reasons:

- By using lowercase snake_case, we completely eliminate the the troubleshooting permutations involved with “Hmm, it’s not working. I wonder if the case matters in the {URL, headers, JSON object names, query parameters, etc}?” Just avoid it all together by choosing snake_case and save XYZ lots of wasted cumulative hours on an avoidable troubleshooting permutation.
- Readability for consumers
- APIs are agnostic to any programming language, so we don’t use that as a reason to go one way or the other with case patterns

### Paging Responses

Use page and per_page query parameters to make it easy for developers to paginate objects. We copy the GitHub API v3 approach almost exactly: <https://developer.github.com/v3/#pagination>

- The per_page query parameter determines the maximum number of objects returned.
- The page query parameter should determine the ‘page’.
- Note that page numbering is 1-based and that omitting the ?page parameter will return the first page.

For example, if you have `per_page=10` and `page=2`, then the API would return the 11th-20th element in the collection.

It is more common, well understood in leading databases, and easy for developers.

## Versioning

### Major or Minor?

If you don’t break backwards compatibility, then you trigger a minor version only. Examples (not limited to):

- Any change to the underlying plumbing behind the service (really just so you can have release notes). Some people handle this with a patch release (x.y.z where z == patch) but we recommend creating a new minor version for such things (patch being for bugs and smaller things).
- Introduce a new verb to a method (GET, PUT, POST, DELETE)
- Adding a new method (usually a new URI path)
- Adding to an existing response

If you break backward compatibility then you trigger a new version. Examples (not limited to):

- Change URI
- Remove or modify existing parts from the response
- Remove or modify methods
- Altering the expected data in any way

### Where Does the Version Go?

A Version goes in the URI. Only a major version has a “v” in front of it. Version should come after the first URI element (what Enterprise Services calls the “API” name). Don’t put it in the header.

Examples:

- **Do** api.abc.com/products/v1/
- **Do** api.abc.com/order_shipments/v2/
- **Don’t** api.abc.com/v1/products/
- **Don’t** api.abc.com/v1.1/products/
- **Don’t** api.abc.com/products/
