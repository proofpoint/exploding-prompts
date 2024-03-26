# Example Usage
`exploding-prompts render ./examples/alternative_sentiment ./out`

`exploding-prompts render ./examples/alternative_sentiment ./out -o root`

`exploding-prompts render ./examples/alternative_sentiment ./out -o root -f model_name=mistral -f label_alternative_name=passive`

`exploding-prompts render ./examples/q_and_a ./out -f question_name=who`

`exploding-prompts render ./examples/q_and_a ./out -f model_name=mistral`

`exploding-prompts render ./examples/q_and_a ./out -f model_name=mistral -f question_name=who`
