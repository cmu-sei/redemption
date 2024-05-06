# <legal>
# 'Redemption' Automated Code Repair Tool
#
# Copyright 2023, 2024 Carnegie Mellon University.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
# INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
# UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
# PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
# THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
# KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
# INFRINGEMENT.
#
# Licensed under a MIT (SEI)-style license, please see License.txt or
# contact permission@sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public
# release and unlimited distribution.  Please see Copyright notice for
# non-US Government use and distribution.
#
# This Software includes and/or makes use of Third-Party Software each
# subject to its own license.
#
# DM23-2165
# </legal>

######################################################################
# Example usage:
# python3 ask_gpt_msc12.py /host/data/test/git.cppcheck.MSC12-C.alerts.json /host/data/test/func_bounds.json -b /oss/git/ --chat-dir /host/data/test/llm/
######################################################################


import os, sys, time, json, argparse, hashlib, re
import pdb
stop = pdb.set_trace

sys.path.append('/host/code/acr')
from util import *
from make_run_clang import read_json_file
from get_enclosing_func import get_enclosing_func

import tiktoken
tokenizer = tiktoken.encoding_for_model("gpt-4")

prompt_msc12c = (
r"""
I want you to adjudicate a static-analysis alert.
The alert concerns CERT Secure Coding Rule MSC12-C: Detect and remove code that has no effect or is never executed.
Statements or expressions that have no effect should be identified and removed from code.

Alert details:
{alert_details}

The flagged line of code is marked `// Line {line_num}` in the code below.

If the alert is a true positive, say `{{"verdict": "true", "rationale": "%s"}}` at the end of your response.
If the alert is a false positive, say `{{"verdict": "false", "rationale": "%s"}}`.
If you are uncertain, say `{{"verdict": "uncertain", "rationale": "%s"}}`.
For `{{"rationale": "%s"}}`, replace `%s` with a very-brief one-sentence rationale.

If code is live in any build, then it should not be considered dead; e.g., an alert that flags an `assert` because it is dead in the release build should be marked as a false positive.

A label that is created as a result of a macro expansion should not be considered a violation of MSC12-C even if it is never used.

Below, I provide the function that contains the flagged line of code.  If parts of the function have been elided, the elided parts are marked by a line consisting of "...".
```
{code_snippet}
(Note that the function might use macros defined elsewhere and not provided above.)
```
"""
)

prompt_useless_asgn = (
r"""
The following static-analysis alert concerns CERT Secure Coding Rule MSC12-C: Detect and remove code that has no effect or is never executed.
"Statements or expressions that have no effect should be identified and removed from code."

Alert details:
{alert_details}

The flagged line of code is marked `// Line {line_num}` in the code below.

1. Identify the variable that is flagged by the alert.
2. Identify whether the variable ever has its address taken (such as by the `&` operator). If it does, then consider the alert a false positive and print the line where the variable's address is taken.
3. Identify whether the variable is read after the flagged assignment.  If it is, then consider the alert to be false positive and print the line where the variable is read after the flagged line.  (This line must contain the variable as an rvalue.)  (Here, "after" means temporally after, not lexically after; i.e., beware of GOTOs and loop backjumps.)  If the variable is read on a line that is lexically subsequent to the flagged line, then indicate roughly how many lines below the flagged line it is.  If it is lexically above the flagged line, then indicate the backjump taken to reach it.
4. If none of the above caused you to consider the alert to be a false positive, then consider the alert to be a true positive.

You may assume that no macro expansions include the flagged variable (unless the variable is an argument to the macro).

If the alert is a true positive, say `{{"verdict": "true", "rationale": "%s"}}` at the end of your response.
If the alert is a false positive, say `{{"verdict": "false", "rationale": "%s"}}`.
If you are uncertain, say `{{"verdict": "uncertain", "rationale": "%s"}}`.
For `{{"rationale": "%s"}}`, replace `%s` with a very-brief one-sentence rationale.

Below, I provide the entirety of the function that contains the flagged line of code:
```
{code_snippet}
```
"""
)


openai_client = None

def get_json_string_value(key, blob):
    m = re.search(f'"{key}": "([^"]*)"', blob)
    if not m:
        return None
    return m.group(1)

def main():
    API_key_help = "Before running, set the environment variable 'OPENAI_API_KEY' to an API key that you create via https://platform.openai.com/api-keys/."
    parser = argparse.ArgumentParser(description="Asks GPT-4 to adjudicate the first alert that lacks a verdict.  " + API_key_help)
    parser.add_argument("alerts_file", type=str, help="alerts.json")
    parser.add_argument("func_bounds", type=str, help="func_bounds.json")
    parser.add_argument("-b", "--base-dir", type=str, help="base dir")
    parser.add_argument("-o", type=str, help="Output file (defaults to alerts_file if omitted)")
    parser.add_argument("--chat-dir", type=str, required=True, help="Dir to write chat logs")
    args = parser.parse_args()

    if (args.o is None):
        args.o = args.alerts_file
    func_bounds = read_json_file(args.func_bounds)
    alerts = read_json_file(args.alerts_file)
    assert(os.path.isdir(args.chat_dir))

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: Missing environment variable.  " + API_key_help)
        sys.exit(1)

    def ask_alert(alert, code_snippet):
        alert_details = {key: alert[key] for key in ['line', 'column', 'tool', 'checker', 'message']}
        alert_details = json.dumps(alert_details, indent=2)
        line_num = alert["line"]
        if alert["checker"].startswith("uselessAssignment"):
            prompt = prompt_useless_asgn.format(**vars())
        else:
            prompt = prompt_msc12c.format(**vars())
        print(prompt)
        messages = [
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.\n" +
                                          "Knowledge cutoff: 2021-09\n" + "Current date: 2023-09-09"},
            {"role": "user", "content": prompt},
        ]
        print(f"File: {alert['file']}")
        print_progress("Asking GPT-4...")
        global openai_client
        if openai_client is None:
            from openai import OpenAI
            openai_client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
        chat_completion = openai_client.chat.completions.create(
            #model="gpt-4-0125-preview",
            model="gpt-4-turbo-preview",
            messages=messages
        )
        print_progress("Done!")
        #print(chat_completion)
        print("="*78)
        answer = chat_completion.choices[0].message.content
        print(answer + "\n")
        chat_filename = hashlib.sha256(answer.encode("utf-8")).hexdigest()[:24] + ".txt"
        alert["llm_output_file"] = chat_filename
        with open(os.path.join(args.chat_dir, chat_filename), "w") as chatfile:
            chatfile.write(answer + "\n")
        for key in ["verdict", "rationale"]:
            value = get_json_string_value(key, answer)
            if value is None:
                print(f"Error: No {key}!")
            else:
                alert[key] = value


    for alert in alerts:
        if alert.get("verdict") in ["","???"] and alert.get("rationale") in ["", "???"]:
            filename = alert["file"]
            if args.base_dir:
                filename = os.path.join(args.base_dir, alert["file"])
            code_snippet = get_enclosing_func(filename, int(alert["line"]), func_bounds)
            num_tok = len(tokenizer.encode(code_snippet))
            if num_tok > 5000:
                num_lines = code_snippet.count("\n")
                print(json.dumps(alert, indent=2))
                print(f"Error: function snippet is too big ({num_tok} tokens, {num_lines} lines)!")
                continue
            if not code_snippet:
                print(json.dumps(alert, indent=2))
                print("Error: Couldn't find containing function!")
                continue
            else:
                ask_alert(alert, code_snippet)
            break


    with open(args.o, "w") as outfile:
        outfile.write(json.dumps(alerts, indent=2) + "\n")

program_start_time = time.time()

def print_progress(msg):
    elapsed_time = time.time() - program_start_time
    print("[%6.2f sec] %s" % (elapsed_time, msg))

if __name__ == "__main__":
    main()
