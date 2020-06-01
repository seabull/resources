#### Pattern Matching

- assignment

  ``` Scala
  case class Animal(name: String, age: Int, classification: Classification)
  val animal = Animal("Jerry", 8, Classification("Mouse", "Mammal"))
  val Animal(name, _, species) = animal
  ```

- Embedded matching

  ```scala
  people match {
    case Seq(a, b, rest @ _*) => s"First two persons are $a and $b, the rest are $rest"
    case _ => s""
  }
  ```

- unapply/unapplySeq

  ```scala
  case class Animal(name: String, species: String)
  // This is used by pattern matching!
  object FarmAnimal {
    def unapply(animal: Animal): Option[String] = {
      if animal.species == "Cow" {
        Some(animal.name)
      } else {
        None
      }
    }
  }
  def namesOfFarmAnimals(animals: Seq[Animal]): Seq[String] = {
    animals.filter {
      case FarmAnimal(_) => true
      case _ => false
    }.map {
      case FarmAnimal(name) => name
      case _ => None
    }
  }
  def moveToFarm(myAnimals: Seq[Animal]): Seq[Animal] = {
    
  }
  object FarmTask {
    def unapply(animal: Animal): Option[(Animal, String)] = {
      if animal.species == "Cow" {
        Some(animal, "milking")
      } else {
        None
      }
    }
  }
  object FarmTasks {
    def unapplySeq(animal: Animal): Option[Seq[String]] = {
      if animal.species == "Cow" {
        Some(Seq("milking", "feeding", "task3"))
      } else {
        None
      }
    }
  }
  ```

  

#### Partial Functions

- PartialFunction, isDefinedAt, orElse, applyOrElse

- ```Scala
  case class Animal(name: String, species: String)
  val santiago = Animal("Santiago", "Cat")
  val cleo = Animal("Cleo", "Dog")
  val meow: PartialFunction[Animal, String] = {
    case Animal(_, "Cat") => println("Cat"); "Meow"
    case Animal(_, "Tiger") => println("Tiger"); "Tiger"
  }
  meow(cleo)  // Error with match
  meow.isDefinedAt(cleo)  // false
  meow.isDefinedAt(santiago)  // true
  meow.isDefinedAt(Animal("A", "Tiger")) // true
  moew(Animal("A", "Tiger"))
  val woof: PartialFunction[Animal, String] = {
    case Animal(_, "Dog") => "Woof"
  }
  val speak = meow orElse woof
  speak(cleo)
  speak(Animal("A", "Cat"))
  ```

- 

#### Collection Features

- collect, collectFirst, partition, groupBy, lift (in addition to map, filter, flatMap)

- Sorting collections

  - Sorted, sortWith, sortBy

- ```scala
  sealed trait Species
  case object Cow extends Species
  case object Horse extends Species
  case object Chicken extends Species
  case object Dog extends Species
  case object Cat extends Species
  case object Wolf extends Species
  
  case class Animal(name: String, age: Int, species: Species)
  val animals = Seq(
  	Animal("Babs", 12, Chicken),
  	Animal("Lady", 4, Chicken),
  	Animal("Babsie", 9, Cow),
  	Animal("Bessy", 12, Cow),
  	Animal("Lettie", 6, Cow),
  	Animal("Douglas", 12, Horse),
  	Animal("Cleo", 12, Dog),
  	Animal("Bonnie", 9, Dog),  
  	Animal("Santiago", 12, Cat),
  	Animal("Athena", 3, Cat)
  )
  
  Seq(4,56,67,62,7,5).sorted
  animals.sorted // error
  animals.sortWith(_.age < _.age)
  animals.sortBy(_.age)
  
  implicit val animalOrdering = Ordering.by[Animal, Int](_.age)
  ```

- 

#### For comprehensions

- ```scala
  for {
    animal <- animals
    if animal.age >= 10
  } yield {
    animal.name
  }
  
  for {
    animal <- animals
    _ = println(animal)
    age = animal.age
    if age >= 10
    _ = println(animal)
  } yield {
    animal.name
  }
  
  for {
    Animal(name, age, _) <- animals
    if age >= 10
  } yield {
    name
  }
  
  
  ```

#### Function Declaration Tricks

- All scala functions are instances of FUNCTIONX Types

- ```scala
  val doubler: Function1[Int, Int] = (x: Int) => 2 * x
  // equivalent of 
  /* 
  new Function1[Int, Int] {
  override def apply(x: Int) = 2 * x
  }
  */
  ```

- 

- Default Arguments, Pass-by-Name, pass-by-name for cleaner DSL

- ```scala
  def makeAnimal(name: String, age: Int = 0, species: Option[String] = None): String = {
    s"Animal $name is $age years old ${species.map { s => " and they are a " + s } getOrElse ""}."
  }
  makeAnimal("Alex", species = Some("Dog"))
  def makeAnimal2(name: String, age: Int = 0, species: Option[String]): String = {
    s"Animal $name is $age years old ${species.map { s => " and they are a " + s } getOrElse ""}."
  }
  makeAnimal2("Alex", species = Some("Dog"))
  makeAnimal2("Alex", 0, Some("Dog"))
  
  def youngName(name: String): String = {
    println("creating young name:")
    "young" + name
  }
  def oldName(name: String): String = {
    println("creating old name:")
    "old" + name
  }
  
  def youngOrOld(age: Int, youngName: String, oldName: String) = {
    if (age < 10) {
      youngName
    } else {
      oldName
    }
  }
  youngOrOld(12, youngName("Alex"), oldName("Bob"))  
  
  def youngOrOld2(age: Int, youngName: ()=>String, oldName: ()=>String): String = {
    if (age < 10) {
      youngName
    } else {
      oldName
    }
  }
  youngOrOld(12, youngName("Alex"), oldName("Bob"))  // Error
  
  // Call by Name
  def youngOrOld3(age: Int, youngName: =>String, oldName: =>String): String = {
    if (age < 10) {
      youngName
    } else {
      oldName
    }
  }
  youngOrOld3(12, youngName("Alex"), oldName("Bob")) 
  
  // Patterns to wraps things around, e.g. exception handling, logging
  def printArithmeticErrors[T](fn: =>T): Option[T] = {
    try {
      Some(fn)
    } catch {
      case arithmeticException: ArithmeticException =>
      	println(arithmeticException)
  	    None
    }
  }
  printArithmeticErrors(5/0)
  printArithmeticErrors {
    (0 to 5).map(5/_)
  }
  ```

- Exception

- ```scala
  import scala.util.control.Exception
  import java.text.{SimpleDateFormat, ParseException}
  import java.util.Date
  
  // The following two are equivalent
  handling(t) by g apply f 
  try { f } catch { case _ : t => g }
  
  // e.g.
  def parse(s: String) : Date = new SimpleDateFormat("yyyy-MM-dd").parse(s)
  def parseDate = parse(System.getProperty("foo.bar"))
  
  val date = handling(classOf[PE], classOf[java.lang.NullPointerException]) by (_ => new Date) apply parseDate
  ```

- 

#### Advanced

- trailrec

- ```scala
  {
    sealed trait TreeEntry
    case class Branch(children: Seq[TreeEntry]) extends TreeEntry
    case class Leaf(content: String) extends TreeEntry
  }
  
  val t = Branch(Seq(Leaf("hello"), Branch(Seq(Leaf("hi"), Leaf("bye")))))
  
  def uniqueContent(root: TreeEntry): Set[String] = {
    root match {
  		case Branch(children) => children.foldLeft(Set[String]())(_ ++ uniqueContent(_))
      case Leaf(content) =>
  	    Set(content)
    }
  }
  uniqueContent(t)
  var deepNest = Branch(Seq.empty)
  // create a deep nested tree
  for (i <- 1 to 4000) { deepNest = Branch(Seq(deepNest)) }
  
  uniqueContent(deepNest) // stack overflow error
  
  @annotation.tailrec def trUniqueContent2(currentLevel: Seq[TreeEntry], seenSoFar: Set[String] = Set.empty): Set[String] = {
    currentLevel match {
  		case Seq(Branch(children), rest @ _*) => 
      	trUniqueContent2(children ++ rest, seenSoFar)
      case Seq(Leaf(content), rest @ _*) =>
  	    trUniqueContent2(rest, seenSoFar + content)
      case _ => seenSoFar
    }
  }
  trUniqueContent2(Seq(t))
  trUniqueContent2(Seq(deepNest))
  
  
  ```

- Jump Table and annotation.switch

- ```scala
  (5: @annotation.switch) match {
    case 5 => "Hello"
    case 3 => "bye"
    case _ => "done"
  }
  
  // ammnite
  // interp.configureCompiler(_settings.nomarnings.value = false) 
  case class Test(in: String)
  (Test("hai") : @annotation.switch) match {
    case Test("hai") => "hai"
    case Test("bai") => "bai"
    case _ => "done"
  }
  ```

- Value classes: one attribute and extends AnyVal

- ```scala
  case class MyValue(val int: Int) extends AnyVal
  class MyValue2(val int: Int) extends AnyVal {
    def withExtra5 = int + 5
  }
  trait MyUniversalTrait extends Any {
    def int: Int
    def withExtra5 = int + 5
  }
  
  class MyValue3(val int:Int) extends AnyVal with MyUniversalTrait
  ```

- Implicit Parameters

- ```scala
  // check implicit in scope
  implicitly[String]
  implicitly[Option[Int]]
  ```

- Typeclass [Explained](https://scalac.io/typeclasses-in-scala/)

- ```scala
  trait Printable[T] {
    def print(item: T): Unit
  }
  val intPrintable = new Printable[Int] { def print(item: Int) = { println(item) }} // TypeClass i.e. Int Class
  
  trait Adder[T] {
    def add(a: T, b: T): T
  }
  
  object Adder {
    // "Summoner" method
    def apply[A](implicit ev: Adder[A]): Adder[A] = ev
  
    // "Constructor" method
    //def instance[A](func: A => List[String]): CsvEncoder[A] = new CsvEncoder[A] {
    //    def encode(value: A): List[String] =
    //      func(value)
    //}
    def instance[A](func: (A, A) => A): String = new Adder[A] {
        def add(valueA: A, ValueB: A): A = func(valueA, valueB)
    }
  
    // Globally visible type class instances
    implicit val intAdder = instance[Int]( (a,b) -> a + b)
  }
  
  def addTwoThings[T](a: T, b: T)(implicit adder: Adder[T]) = {
    adder.add(a, b)
  } // Need to define a Adder T Class (TypeClass) to use this function
  
  
  def addTwoThings[T](a: T, b: T)(implicit adder: Adder[T], printable: Printable[T]) = {
    printable.print(a)
    printable.print(b)
    adder.add(a, b)
  }
  
  trait Show[A] {
    def show(a: A): String
  }
  
  object Show {
    // "Summoner" method
  	// def apply[A](implicit enc: CsvEncoder[A]): CsvEncoder[A] = enc
    def apply[A](implicit sh: Show[A]): Show[A] = sh
  
    // "Constructor" method
    //def instance[A](func: A => List[String]): CsvEncoder[A] = new CsvEncoder[A] {
    //    def encode(value: A): List[String] =
    //      func(value)
    //}
    def instance[A](func: A => String): String = new Show[A] {
        def show(value: A): String = func(value)
    }
  
    // Globally visible type class instances
    
    //needed only if we want to support notation: show(...)
    def show[A: Show](a: A) = Show[A].show(a)
  
    implicit class ShowOps[A: Show](a: A) {
      def show = Show[A].show(a)
    }
  
    //type class instances
    implicit val intCanShow: Show[Int] =
      int => s"int $int"
  
    implicit val stringCanShow: Show[String] =
      str => s"string $str"
  }
  ```

- Implicit Class and object extensions (implict class and value class)

- ```scala
  implicit class MagicInterpolater(val sc: StringContext) {
    def m(parameters: Any*) = {
      println(sc.parts)
      println(parameters)
    }
  }
  
  val name = "Alex"
  m"Hello $name"
  m"Hello $name $name world"
  
  implicit class MagicInterpolater(val sc: StringContext) {
    def m(parameters: Any*) = {
      sc.parts.zipAll(parameters, "", "") match {
        case ("", param) => param
        case (part, "") => part
        case (part, param) => s"$part:MAGIC:$param"
      }.mkString("\n")
    }
  }
  
  implicit class PoundifyStrings(val string: String) extends AnyVal {
    def poundify: String = {
      string.replace(" ", "#")
    }
  }
  "test test test".poundify
  ```

- Interop with Java, Profiling

- ```scala
  import scala.collection.JavaConverters._
  ```

- [Types](https://kubuszok.com/2018/kinds-of-types-in-scala-part-1/)

  - Scala has also the notion of the top and bottom types. The top type - a type we don’t have any assertions about, which contains any other type - is `Any`. In Java, the closest thing would be an `Object`, except it is not a supertype for primitives. Scala’s `Any` is a supertype for both objects (`AnyRef`) and primitives (`AnyVal`). When we see `Any` as an inferred type, it usually means we messed up and combined two unrelated types.

    The bottom type - a type which is a subtype of all others, and has no citizen - in Scala is `Nothing`. We cannot construct a value of type `Nothing`, so it often appears as a parameter of empty containers or functions that can only throw.

    (Quite often I see that `Null` is mentioned as another bottom type in Scala together with `Nothing`. It is a type extending everything that is an `Object` on JVM. So it is kind of like `Nothing` without primitives, `Unit`/`void`, and functions that only throws).

    Also, a word about functions. In Scala we make a distinction between a function and a method. A **function type** is a value, which can be called:

    A **method**, on the other hand, **is not a value**. It cannot be assigned, or directly passed, though via a process called **eta-expansion** a method can be turned into a function.

    ```scala
    val times2: Int => Int = x => x * 2
    def times2(x: Int): Int = x * 2
    // val y = def times2(x: Int): Int = x * 2 - error!
    val y = { def times2(x: Int): Int = x * 2 } // Unit
    // however
    val z: Int => Int = times2 _ // works!
    ```

    Less accurate, but simpler version: a function is an instance of some `Function0`, `Function1`, …, `Function22` trait, while a method is something bound to a JVM object. We make a distinction because authors of Scala haven’t solved the issue in a more elegant way.

  - Algebraic Data Types
    When we think of types as a sets, there are 2 special constructions, that help us build new sets from existing ones, which complement each other. One is a [Cartesian product](https://en.wikipedia.org/wiki/Cartesian_product) and the other is a [disjoint union/disjoint set sum (coproduct)](https://en.wikipedia.org/wiki/Disjoint-set_data_structure).
    Product types and sum types together are known as **algebraic data types**.

    Scala 2.x doesn’t allow to actually build up an union from already existing types. If we want to let compiler know that types should form a coproduct, we need to use a **sealed hierarchy**:

    ```scala
    sealed trait Either[+A, +B] {}
    case class Left[+A, +B](a: A) extends Either[A, B]
    case class Right[+A, +B](b: B) extends Either[A, B]
    
    sealed trait Option[+A] {}
    case class Some[A](value: A) extends Option[A]
    case object None extends Option[Nothing]
    ```

  - We can calculate a sum of sets (sum type), a Cartesian product of sets (product type), why not an intersection? We can declare a type belonging to several types using… `with` keywords (yup, it’s more than just a mixin!).
    **the order of composing type using `with` does not matter**

  - ```scala
    trait Str { def str: String }
    trait Count { def count: Int }
    
    def repeat(cd: Str with Count): String =
      Iterator.fill(cd.count)(cd.str).mkString
    
    repeat(new Str with Count {
      val str = "test"
      val count = 3
    })
    // "testtesttest"
    ```

  - Diamond problem, Solution: Trait Linearization

  - ```scala
    trait A { def value = 10 }
    trait B extends A { override def value = super.value * 2 }
    trait C extends A { override def value = super.value + 2 }
    (new B with C {}).value // ???
    (new C with B {}).value // ???
    // trait linearization
    
    trait X extends A with B with C
    
    trait AnonymousB extends A {
      // B overrides A
      override def value = super.value * 2
    }
    trait AnonymousC extends AnonymousB {
      // C overrides AnonymousB
      override def value = super.value + 2
    }
    trait X extends AnonymousC
    
    (new B with C {}).value // (10 * 2) + 2 = 22 
    (new C with B {}).value // (20 + 2) * 2 = 24
    ```

  - ## Kinds and higher-kinded-types

    These *types of types* (a type, a type constructor, etc) are known as [**kinds**](https://en.wikipedia.org/wiki/Kind_(type_theory)). Scala let us investigate them in REPL using `:kind`

  - Type Constraints

    - `<:` denotes an upper bound in type parameters. 
    - There is also a notation for lower bound, `>:`
    - `<:<` - let us require that one type is a *subclass* the other. It is defined inside a `scala.Predef`.

    ```scala
    def upcast[A, B](set: Set[A])(
      implicit ev: A <:< B
    ): Set[B] = set.map(ev(_))
      
    upcast[Member, User](Set(m: Member)) // Set[User]
    ```

    - `=:=` - let us require that one is *equal* to the other.

      ```scala
      def update[A, B](set: Set[A])(f: A => B)(
        implicit ev: A =:= B
      ): Set[B] = set.map(f)
        
      val members: Set[Member]
        
      update[Member, Member](members)(identity) // ok
      update[Member, User](members) { member =>
        member: User
      } // compilation error!
      ```

      

    - `=:!=` - provided by shapeless. Proves, that types are *different*.

  - Variance

    - Invariance means, that even if `B <: A` then `Option[B]` still cannot be substituted for `Option[A]`. It is a default and a good one!
    - if `B >: A` then `F[B] >: F[A]` is called **covariance**. To mark a type parameter as covariant we use `+`
    - Case where we want to say that `A <: B` implies `F[B] >: F[A]` is called **contravariance** as it is an opposition of covariance. We denote it with `-` sign

  - F-bound Types

  - Structural and refined Types
    We can call `User` a **structural type**. It is an interesting way of implementing a type, one where compiler checks if object has all the right methods and fields instead of scanning the class hierarchy. A problem with such approach is that in runtime Scala has to use a runtime reflection to access these fields, so it comes with a performance penalty.

    ```scala
    type User = {
      val name: String
      val surname: String
    }
    case class Somebody(name: String, surname: String)
    
    def needUser(user: User): Unit
    
    needUser(Somebody("test", "test")) // works!
    
    trait X { val x: String }
    type Y = { val y: Int }
    val z: X with Y = new X { val x = "test"; val y = 0 }
    ```

  - Path-dependent Types
    **Path-dependent types** are way of stating that type of one object, depends on another object. It is a limited version of more generic idea of [dependent types](https://en.wikipedia.org/wiki/Dependent_type).
    To create a path-dependent type, all we need is to declare a type inside another type! It doesn’t have to be a class

    ```scala
    class Game {
      
      case class Card(color: String, value: String)
      case class Player(name: String)
      
      def getPlayers: Set[this.Player] = ???
      
      def getCards: Set[this.Card] = ???
      
      def playerPlayCard(player: this.Player, card: this.Card): Unit = ???
    }
    
    val game1 = new Game
    val game2 = new Game
    game1.getPlayers // Set[game1.Player]
    game2.getPlayers // Set[game2.Player]
    
    game1.playerPlayCard(game2.getPlayers.head,
                         game2.getCards.head) // fails!
    
    class X {
      type Y = String
      val y: Y = "y"
    }
    
    val x1 = new X
    val x2 = new X
    // However, if it’s just a type alias, Scala can prove that 2 types are the same, and so it will not help us much:
    
    def y(x: X)(y: x.Y): Unit = ()
    
    y(x1)(x2.y) // no complaints: x1.Y = String = x2.Y
    
    // unless we make it a little less obvious, that the types are equal:
    trait X {
      type Y = String
      val y: Y = "y"
    }
    
    class X2 extends X
    
    val x1 = new X2
    val x2 = new X2
    
    y(x1)(x2.y) // fails!
    ```

    ```scala
    //OK, but what if we wanted to lose our requirements at some point?
    
    def takeAnyPlayer(p: ???): Unit
    //We need to indicate a way of passing path-dependent type without its the context if needed. Such ability is granted to us via #:
    
    def takeAnyPlayer(p: Game#Player): Unit
    
    // At this point there is very little we know for certain about our p. Scala most won’t be able to tell what is the exact type even if it would be obvious to you from the code. If there were some type constraints about the type, that would be guaranteed, you can rely on it. But anything that comes with the specification of path-dependent type is lost:
    
    
    trait X {
      type Y <: AnyVal { def toLong: Long }
      val y: Y
    }
    
    val x1 = new X {
      override type Y = Int
      override val y: Y = 1
    }
    val x2 = new X {
      override type Y = Long
      override val y: Y = 1L
    }
    
    x1.y * x1.y // 1: Int
    x2.y * x2.y // 1: Long
    ```

  - Kind projector/type lambda

    ```
    scala> :kind ({ type T[A] = Either[String, A] })#T
    scala.util.Either[String,?]'s kind is F[+A]
    ```

    We start with `Either[_, _]` and we want to partially apply `String` as the first type parameter. In order to do so, we:

    - create a type alias `T[A] = Either[String, A]`, which creates a parametric type `T[A]` with one type parameter,
    - we put it inside a structural type to create an opportunity for creating a path-dependent type,
    - finally we extract `T` as a path-dependent type, such that Scala can tell its specific type exactly,
    - since we didn’t applied type parameters, we end up with a single parameter type constructor,
    - we achieved partial-application of a type parameters to a type constructor, aka **type lambda** or **kind projection**.

  - Self Types
    Mixins. Sometimes we want to add some functionality to existing class and traits are a great way of achieving that:

    ```scala
    class Producer {
      def produce: Int = 1
    }
    
    trait DoubleProducer extends Producer {
      override def produce: Int = super.produce * 2
    }
    
    trait IncreaseProducer extends Producer {
      override def produce: Int = super.produce + 1
    }
    
    class MyProducer extends Producer with DoubleProducer with IncreaseProducer
    
    (new MyProducer).produce // 3
    
    // Mixin
    trait Producer {
      def produce: Int
    }
    
    // Don't need to extends Producer
    trait DoubleProducer { self: Producer =>
      override def produce: Int = super.produce * 2
    }
    ```

    Self-types, might be used to enforce ordering of [low-priority implicits](https://kubuszok.com/2018/implicits-type-classes-and-extension-methods-part-4/#troublesome-cases):

    

#### Shapeless

- [Shapeless and Spark](https://medium.com/build-and-learn/is-shapeless-worth-it-what-is-shapeless-anyway-900cba6b717a)

- [Get started with Shapeless](https://jto.github.io/articles/getting-started-with-shapeless/)

- [a blog](https://lepovirta.org/posts/2015-10-30-solving-problems-in-a-generic-way-using-shapeless.html)

- [Spark StructType encoder using shapeless](https://benfradet.github.io/blog/2017/06/14/Deriving-Spark-Dataframe-schemas-with-Shapeless)

- Idiomatic Type Class definition

  ```scala
  trait CsvEncoder[A] {
     def encode(value: A): List[String]
  }
  
  object CsvEncoder {
  // "Summoner" method
  def apply[A](implicit enc: CsvEncoder[A]): CsvEncoder[A] =
  enc
    // "Constructor" method
  def instance[A](func: A => List[String]): CsvEncoder[A] = new CsvEncoder[A] {
        def encode(value: A): List[String] =
          func(value)
  }
    // Globally visible type class instances
  }
  ```

  

- Instances

- ```Scala
  def createEncoder[A](func: A => List[String]): CsvEncoder[A] = new CsvEncoder[A] {
      def encode(value: A): List[String] = func(value)
    }
  implicit val stringEncoder: CsvEncoder[String] =
    createEncoder(str => List(str))
  implicit val intEncoder: CsvEncoder[Int] =
    createEncoder(num => List(num.toString))
  implicit val booleanEncoder: CsvEncoder[Boolean] = createEncoder(bool => List(if(bool) "yes" else "no"))
  
  ```

- ***Aux type aliases*** 

  ```scala
  implicit def genericEncoder[A, R](
    implicit
    gen: Generic[A] { type Repr = R },
    enc: CsvEncoder[R]
  ): CsvEncoder[A] =
    createEncoder(a => enc.encode(gen.to(a)))
  ```

  Type refinements like Generic[A] { type Repr = L } are verbose and difficult to read, so shapeless provides a type alias Generic.Aux to rephrase the type member as a type parameter: 

  ```scala
  package shapeless
  object Generic {
    type Aux[A, R] = Generic[A] { type Repr = R }
  ```

  } 

  Using this alias we get a much more readable defini􏰀on: 

  ```scala
  implicit def genericEncoder[A, R](
    implicit
    gen: Generic.Aux[A, R],
    env: CsvEncoder[R]
  ): CsvEncoder[A] =
    createEncoder(a => env.encode(gen.to(a)))
  ```

  Note that the Aux type isn’t changing any seman􏰀cs—it’s just making things easier to read. This “Aux pattered􏰁ern” is used frequently in the shape- less codebase. 

- Taking all of this into account, we can write a common skeleton for deriving type class instances as follows. 

  First, define the type class: 

  ```scala
   trait MyTC[A]
  ```

  Define primi􏰀ve instances: 

  ```scala
  implicit def intInstance: MyTC[Int] = ???
  implicit def stringInstance: MyTC[String] = ???
  implicit def booleanInstance: MyTC[Boolean] = ???
  ```

  Define instances for HList: 

  ```scala
  import shapeless._
  implicit def hnilInstance: MyTC[HNil] = ???
  implicit def hlistInstance[H, T <: HList](
    implicit
    hInstance: Lazy[MyTC[H]], // wrap in Lazy
    tInstance: MyTC[T]
  ): MyTC[H :: T] = ???
  ```

  If required, define instances for Coproduct: 

  ```scala
  implicit def cnilInstance: MyTC[CNil] = ???
  implicit def coproductInstance[H, T <: Coproduct](
    implicit
    hInstance: Lazy[MyTC[H]], // wrap in Lazy
    tInstance: MyTC[T]
  ): MyTC[H :+: T] = ???
  ```

  Finally, define an instance for Generic: 

  ```scala
  implicit def genericInstance[A, R](
    implicit
    generic: Generic.Aux[A, R],
    rInstance: Lazy[MyTC[R]] // wrap in Lazy
  ): MyTC[A] = ???
  ```

  In the next chapter we’ll cover some useful theory and programming pa􏰁erns to help write code in this style. In Chapter 5 we will revisit type class deriva􏰀on using a variant of Generic that allows us to inspect field and type names in our ADTs. 

- The intui􏰀ve take-away from this is that type parameters are useful as “inputs” and type members are useful as “outputs”. 

- ***Summoner methods versus “implicitly” versus “the”*** 

  Note that the return type on apply is Aux[L, O], not Second[L]. This is important. Using Aux ensures the apply method does not erase the type members on summoned instances. If we define the return type as Second[L], the Out type member will be erased from the return type and the type class will not work correctly. 

  The **implicitly** method from scala.Predef has this behaviour. Compare the type of an instance of Last summoned with implicitly:  

  ```scala
  implicitly[Last[String :: Int :: HNil]]
  // res6: shapeless.ops.hlist.Last[String :: Int :: shapeless. HNil] = shapeless.ops.hlist$Last$$anon$34@651110a2 
  ```

  to the type of an instance summoned with Last.apply: 

  ```scala
  Last[String :: Int :: HNil]
  // res7: shapeless.ops.hlist.Last[String :: Int :: shapeless. HNil]{type Out = Int} = shapeless.ops. hlist$Last$$anon$34@571bb8f6 
  ```

  The type summoned by implicitly has no Out type member. For this reason, we should avoid implicitly when working with dependently typed func􏰀ons. We can either use custom summoner methods, or we can use shapeless’ replacement method, the:

  ```scala
  import shapeless._
  the[Last[String :: Int :: HNil]]
  // res8: shapeless.ops.hlist.Last[String :: Int :: shapeless. HNil]{type Out = Int} = shapeless.ops. hlist$Last$$anon$34@1cd22a69 
  ```

- When coding with shapeless, we are o􏰄en trying to find a target type that depends on values in our code. This rela􏰀onship is called ***dependent typing*.** 

  Problems involving dependent types can be conveniently expressed using im- plicit search, allowing the compiler to resolve intermediate and target types given a star􏰀ng point at the call site. 

  We o􏰄en have to use mul􏰀ple steps to calculate a result (e.g. using a Generic to get a Repr, then using another type class to get to another type). When we do this, there are a few rules we can follow to ensure our code compiles and works as expected: 

  1. We should extract every intermediate type out to a type parameter. Many type parameters won’t be used in the result, but the compiler needs them to know which types it has to unify. 
  2. Thecompilerresolvesimplicitsfromle􏰄toright,backtrackingifitcan’t find a working combina􏰀on. We should write implicits in the order we need them, using one or more type variables to connect them to previ- ous implicits. 
  3. Thecompilercanonlysolveforoneconstraintata􏰀me,sowemustn’t over-constrain any single implicit. 
  4. We should state the return type explicitly, specifying any type param- eters and type members that may be needed elsewhere. Type mem- bers are o􏰄en important, so we should use Aux types to preserve them where appropriate. If we don’t state them in the return type, they won’t be available to the compiler for further implicit resolu􏰀on. 
  5. The Aux type alias pa􏰁ern is useful for keeping code readable. We should look out for Aux aliases when using tools from the shapeless toolbox, and implement Aux aliases on our own dependently typed func􏰀ons. 

- Misc Resources

  - [Stackoverflow disjunction union types](https://stackoverflow.com/questions/3508077/how-to-define-type-disjunction-union-types)
  - [Enums](https://pedrorijo.com/blog/scala-enums/)
  - [Type Level programming explain](http://gigiigig.github.io/)
  - [shapeless for cross layer conversion blog](https://blog.softwaremill.com/how-not-to-use-shapeless-for-cross-layer-conversions-in-scala-9ac36363aed9)
  - [Type Level Programming in Shapeless](https://apocalisp.wordpress.com/2010/06/08/type-level-programming-in-scala/)
  - [spark tips](https://cm.engineering/10-tips-in-writing-a-spark-job-in-scala-cc837149a173)
  - [Denpenency Injection](http://jonasboner.com/real-world-scala-dependency-injection-di/)
  - [Return current type](https://tpolecat.github.io/2015/04/29/f-bounds.html)
  - [Concurrency](https://blog.matthewrathbone.com/2017/03/28/scala-concurrency-options.html)
  - LIbraries
    - [JSON Encoding using argonaut-shapeless](https://github.com/alexarchambault/argonaut-shapeless)