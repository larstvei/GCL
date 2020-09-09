import re
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

def trace2maudestr(trace):
    return '++'.join([event2maudestr(event) for event in trace])

def run_gcl(exp):
    maude_process = start_maude()
    cmd = ('rew in GCL-CONCOLIC-SEMANTICS : ' + exp + ' .\n')
    result = maude_process.communicate(input=cmd.encode())[0].decode()
    runtime_state = result.split("result RuntimeState:")[-1]
    almost_trace, end_state, _ = runtime_state.split("| ")
    almost_trace = almost_trace.split("{")[-1]
    trace = [maudestr2event(event_str) for event_str in almost_trace.split("++")]
    return tuple(trace)

def run_canon(trace):
    maude_process = start_maude()
    cmd = ('red in TRACE : canon(' + trace2maudestr(trace) + ') .\n')
    result = maude_process.communicate(input=cmd.encode())[0].decode()
    raw = re.split(r"result (Label|Trace):", result)[-1]
    almost_trace = raw.split("Maude>")[0]
    trace = [maudestr2event(event_str) for event_str in almost_trace.split("++")]
    return tuple(trace)

def run_eval_path(state, theta):
    maude_process = start_maude()
    cmd = 'rew in EVAL-PATH : eval(' + state + ', path(' + trace2maudestr(theta) + ')) .\n'
    result = maude_process.communicate(input=cmd.encode())[0].decode()
    raw = result.split("result Bool:")[-1]
    hopefully_bool = raw.split("Maude>")[0].strip()
    if hopefully_bool == 'true':
        return True
    if hopefully_bool == 'false':
        return False
    print(result)
    assert(False)

def local_traces(trace):
    res = defaultdict(list)
    for (iota, guard, exp) in trace:
        res[iota].append((iota, guard, exp))
    return res

def nextevent(iota, theta, lt):
    lt1 = lt[iota]
    lt2 = local_traces(theta)[iota]
    if len(lt2) < len(lt1):
        return lt1[len(lt2)]
    return None

def proc(theta):
    res = {'0'}
    for (iota, guard, exp) in theta:
        m = re.match(r'spawn\((\d+( \d+)*)\)', exp)
        if m is not None:
            res.add(m[1])
    return res

def search(theta0, sigma0):
    lt = local_traces(theta0)
    I = {tuple([])}
    for i in range(len(theta0)):
        I2 = I
        I = set()
        for theta in I2:
            for iota in proc(theta):
                e = nextevent(iota, theta, lt)
                if e is not None:
                    theta2 = run_canon(theta + tuple([e]))
                    if theta2 not in I and run_eval_path(sigma0, theta2):
                        I.add(theta2)
    return I

def pretty_print_res(I):
    for theta in I:
        print(' ++\n'.join([event2maudestr(e) for e in theta]))
        print()

# do maude interaction to get a recorded trace
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

if __name__ == '__main__':
    print(test_program_1)

    theta0 = run_gcl(test_program_1)
    sigma0 = test_program_1.split('| ')[1]

    pretty_print_res(search(theta0, sigma0))
