# Inseguendo Fagiani Selvatici: Partial Order Reduction for Guarded Command Languages

This is a Maude implementation of concolic execution for a guarded commands
language. To run the program, be sure to have [Python
3](https://www.python.org/download/releases/3.0/) and the [Maude
system](http://maude.cs.illinois.edu/w/index.php?title=Maude_download_and_installation)
installed first.

Consider the program from Example 5 of the paper (Inseguendo Fagiani Selvatici:
Partial Order Reduction for Guarded Command Languages):

```
{ epsilon
| ('x |-> 0, 'y |-> 0, 'flag |-> true)
| iota< 0, 0 >
(true |> spawn(('x =:= 0 or 'flag) |> 'x := 2 * 'x) ;
 true |> spawn(('x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               true |> 'y := 'y + 1))) }
```

Run the following to get all equivalent traces:

```sh
$ python3 algo.py
```
