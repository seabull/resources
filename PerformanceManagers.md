### Performance Managers

```mermaid
classDiagram
	StageCompletionManager <|-- SparkListener
	StageCompletedEventConsumer <|-- StageMetricEventConsumer
	StageCompletedEventConsumer <|-- LogStageMetricConsumer
	TaskCompletionManager <|-- SparkListener
	TaskCompletedEventConsumer <|-- TaskMetricEventConsumer

	StageCompletionManager : Map consumerRegistery
	StageCompletionManager : addEventConsumer()
	StageCompletionManager : removeEventConsumer()
	StageCompletionManager: onStageCompleted()
	
	TaskCompletionManager : Map consumerRegistery
	TaskCompletionManager : addEventConsumer()
	TaskCompletionManager : removeEventConsumer()
	TaskCompletionManager: onTaskCompleted()


	StageCompletedEventConsumer: execute(stageMetrics: StageMetrics)
	StageMetricEventConsumer : execute(stageMetrics)
	LogStageMetricConsumer : execute(stageMetrics)
	TaskCompletedEventConsumer: execute(taskMetrics: TaskMetrics)
	TaskMetricEventConsumer : execute(taskMetrics)


```

