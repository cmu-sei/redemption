jq -r '.[] | .llm_output_file // empty | select(test("^[0-9a-f]{24}[.]txt$"))' ../*.alerts.json
