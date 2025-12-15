# python-outside-in-testing-strategy-example
an example of how I like to do python diamond testing

```mermaid

flowchart 
    i((Initiator)) -->|Start task| a 
    a -->|Poll for results| i 
    a[REST API] -->|Enqueue task| q[/Queue/]
    a[REST API] <--> db[(Database)]
    q --> |Task config|w[Task worker]
    w --> |Inform on Task Progress|a

```