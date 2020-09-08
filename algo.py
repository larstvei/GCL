from collections import defaultdict
from subprocess import Popen, PIPE, STDOUT

maude_cmd = ['maude', '-no-prelude', '-no-banner', '-no-advise', '-no-wrap', 'gcl.maude']

def start_maude():
    return Popen(maude_cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)

def maudestr2event(event_str):
    event_str = event_str.strip().lstrip('(').rstrip(')')
    iota, rest = event_str.split("[")
    guard, exp = rest.split('|>')
    assert '' not in {iota, guard,  exp[:-1]}
    return (iota, guard.strip(), exp[:-1].strip())

def event2maudestr(event):
    iota, guard, exp = event
    return '(' + iota + '[' + guard + ' |> ' + exp + '])'

def run_gcl(exp):
    maude_process = start_maude()
    cmd = ('rew in GCL-CONCOLIC-SEMANTICS : ' + exp + ' .\n')
    result = maude_process.communicate(input=cmd.encode())[0].decode()
    print(result)
    runtime_state = result.split("result RuntimeState:")[-1]
    almost_trace = runtime_state.split("| ")[0]
    almost_trace = almost_trace.split("{")[-1]
    trace = [maudestr2event(event_str) for event_str in almost_trace.split("++")]
    return trace

def local_traces(trace):
    res = defaultdict(list)
    for (iota, guard, exp) in trace:
        res[iota].append((iota, guard, exp))
    return res

test_program_1 = """
{ epsilon
| ('x |-> 0, 'y |-> 0, 'flag |-> true)
| iota< 0, 0 >
(true |> spawn(('x =:= 0 or 'flag) |> 'x := 2 * 'x) ;
 true |> spawn(('x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               'x := 'x + 2 <| 'flag |> 'x := 'x + -1 ; true |> 'flag := (not 'flag) ;
               true |> 'y := 'y + 1))) }
"""

# do maude interaction to get a recorded trace

def search(theta0, sigma):
    I = {[]}
    for i in range(len(theta0)):
        I2 = I
        I = set()
        for theta in I2:
            for iota in T(theta):
                if nextevent(iota, theta):
                    # Extend is magic and canonicalizes
                    theta2 = extend(theta, nextevent(iota, theta))
                    if theta2 not in I and sigma(path(theta2)):
                        I.add(theta2)
    return I
