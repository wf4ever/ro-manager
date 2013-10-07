
Formalization of checklist evaluation
=====================================

I'm planning to start the formalization process by expressing the checklist evaluation as a pure, strongly-typed function.  I'll use Haskell for this.  The document will be prepared as Literate Haskell with Markdown markup, and processed using `pandoc` - see [http://stackoverflow.com/questions/3473389/lhs-and-markdown-codeblocks]() and [http://johnmacfarlane.net/pandoc/](). This file is (or will be) an executable Haskell program, which can also be converted into an HTML document thus:

    pandoc --from=markdown+lhs --to=html -o checklist-formalization.html checklist-formalization.lhs

In modelling the checklist, I shall focus on the checklist itself, and not consider here the additional logioc that uses _target_ and purpose


Preliminaries
-------------

The following code makes use of certain extensions to the Haskell type system, which are enabled by this directive:

> {-# LANGUAGE RankNTypes, ImpredicativeTypes #-}

The checklist function operates against an instance of `Web`.  Treated for the purposes of checklist evaluation as a read-only medium, a `Web` value is a mapping from `URI`s to `Resources`s (ignoring here the effect of additional HTTP protocol parameters).

> data URI a = URI String (a -> ())

> type URIany = forall a. URI a

> data Resource a = Resource a
> resourceVal (Resource a) = a

> type Web    = forall a. (URI a -> (Resource a, Status))
> type Status = Int   -- value indicates status of resource as HTTP status code

A research object is a web resource with some additional contextual information:

> type ROURI = URI RO

> type RO = ( [URIany], [Assertion] )

> type Assertion = Web -> Bool


Checklist function
------------------

A checklist is modelled as a function whose application to some resource corresponds to evaluating the checklist against the RO denoted by that resource at a particular state of the web:

> type Checklist = Web -> ROURI -> ( Checklist_result, [Item_result] )

> type Checklist_result = Satisfaction_level   -- Maybe more values to come here
> data Satisfaction_level = Fully_satisfied | Nominally_satisfied | Minimally_satisfied | Not_satisfied

> type Item_result = ( Level, Bool, String )

> data Level = MUST | SHOULD | MAY

Here, we see the result of evaluating a checklist is a `Checklist_result` value, and a list of `Item_result` values, which are defined as shown.


Checklist items
---------------

A checklist item corresponds to a single reported requirement in our checklist.  It is a function that takes a `Web` and an `ROURI`, and returns a Boolean (pass/fail) and a descriptive message.

> type Checkitem = Web -> ROURI -> (Bool, String)

Instances of this function embody the "checklist primitives" from which checklist functionality is built up.  Given a list of `Checkitem` values and corresponding `Level` values, a `Checklist` can be constructed in entirely generic fashion.  Thereafter, our focus on checklist capabilities can be focused on the primitives that are used to construct `Checkitem` values:

> makeChecklist :: [ (Level, Checkitem) ] -> Web -> ROURI -> ( Checklist_result, [Item_result] )
> makeChecklist items web rouri = (check_result item_results, item_results)
>   where
>     check_result item_results = foldl check_result_next Fully_satisfied item_results
>       where
>         check_result_next z (MAY,    False, _) = level_min z Nominally_satisfied
>         check_result_next z (SHOULD, False, _) = level_min z Minimally_satisfied
>         check_result_next z (MUST,   False, _) = level_min z Not_satisfied
>         check_result_next z _                  = z
>         level_min Not_satisfied       _                    = Not_satisfied
>         level_min _                   Not_satisfied        = Not_satisfied
>         level_min Minimally_satisfied _                    = Minimally_satisfied
>         level_min _                   Minimally_satisfied  = Minimally_satisfied
>         level_min Nominally_satisfied _                    = Nominally_satisfied
>         level_min _                   Nominally_satisfied  = Nominally_satisfied
>         level_min _                   _                    = Fully_satisfied
>     item_results :: [ Item_result ]
>     item_results     = map item_result items
>     item_result :: (Level, Checkitem) -> Item_result
>     item_result (level, item) = (level, b, s) 
>       where (b, s) = item web rouri


Checklist item primitives
-------------------------

Our checklist primitives depend on an RO defining a context, which consists of a distinguished set of URIs (denoting the resources aggregated by the RO) and a set of assertions about the state of resources in the web (annotations, which are RDF expressions).  The annotations being RDF expressions means that, by way of [RDF semantics](http://www.w3.org/TR/rdf-mt/), they are truth-valued functions over the denotations of the URIs they use.  These denotations in turn are assumed to be reflected by the state of the Web for which they are evaluated, and thus serve as semantic constraints on the assumed state of the Web that is evaluated by a checklist.

The checklist primitive functions are evaluated in the presence of these constraints.


<h3>Queries</h3>

The checklist primitives make extensive use of _queries_.  A query is a pattern that is matched against all of the assertions in the tested RO, and which may result in zero or more _matches_.

@@the formalism in this area needs to be developed into something that links the query with the RO annotations and corresponding Web models.

@@Model-theoretic approach:  a query is a set of assertions, possibly containing existentials variables, that result in zero or more assertions with actual values substituted for the existentials, which are true in every model in which the RO assertions are all true.

@@Proof theoretic approach: assertions and query to graph edges and graph edge patterns respectively.  Query may be unified, datalog-style, against the assertions (and inferred statements) to yield any matches.

Define types for query, query variable and variable substitution (binding):

> type Query        = String
> type Var          = String
> type Substitution = [(Var, URIany)]

Assume the presence of a query-matching function

> match :: Query -> [Assertion] -> [Substitution]
> match q as = undefined   -- placeholder

That is, yielding a list of variable binding sets, where each variable binding set associates a number of variables with corresponding values.  Using a resulting variable binding to define a substitution of values for variables in the query results in an assertion that is entailed by the RO assertions.  Can be evaluated by _unification_ of the query and assertions.

Also assume the presence of a substitution function:

> substitute :: Query -> Substitution -> Assertion
> substitute q s a = undefined   -- placeholder

and a subsumption function:

> subsumes :: [Assertion] -> [Assertion] -> Bool
> subsumes as1 as2 = undefined   -- placeholder

then we have:

    assertions `subsumes` (map (substitute query) (match query assertions))

is `True` for all values for assertion and query

**Note**: as assertions are generally defined by enumeration, the notion of subsumption used here is somewhat simpler than that which is the target of description logic reasoning.  Roughly, whet we use here is a closed-world notion of subsumption, which is much easier to evaluate than an open-world subsumption.  However, if subsumption is taken to include inferable assertions as well as those explicitly stated, then some aspects of reasoning, Description Logic based or otherwise, might be needed to ensure completeness of the subsumption evaluation.


<h3>Simple existence check</h3>

> probe_exists :: Query -> Substitution -> [Assertion] -> Bool
> probe_exists q s as = undefined   -- placeholder

Returns True if the query has at least one binding set that unifies with the RO assertions, and also with the supplied variable bindings

This provides a simple test that checks for the presence of certain information.  (The supplied list of assertions may be empty.)

A checklist item that checks for the existence of statements matching a query can be constructed thus:

> item_exists :: Query -> Checkitem
> item_exists q web rouri = (match, msg)
>   where
>     (ro, sts) = web rouri
>     as        = if (sts >= 200) && (sts <= 299) then (snd $ resourceVal ro) else []
>     match     = probe_exists q [] as
>     msg       = if match then "item_exists test passed" 
>                          else "item_exists test failed"


Checklist item composition
--------------------------

@@TO FOLLOW


