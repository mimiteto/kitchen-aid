# kitchen-aid internals

Kitchen aid supports two modes of execution - command and standard flow.
Command flow is utilising the base command utils - `Result`, `Command`, `CommandHandler` and `CommandMapper`
Standard flow has more advanced toolset.

## Command modules

### Result

Result is a basic component which wraps the result of a command.
Results contain the status, message and list of errors.
It can be extended to provide more data fields. It's best to avoid havinf logic within the result subclasses.

### Command

Commands are basic wrappers around custom "receiving" utilities.
Commands have 3 execution utils:

* `execute` - this is the method that is always called. Within the `execute` method one should configure and run the "receiver" callable and wrap it's result in `Result` object.
* `undo` - this method should be implemented if the command supports undo actions. Undo actions should return a `Result` object, that describes the end resultof the `undo` action. `undo` actions should be safe and should aim to return to the state before `execute`. No additional actions are automatically done on failed `undo`.
* `redo` - this method is not currently handled. If you are implementing it, think of a situation where `undo` completed succesfully and as a side effect `CommandTryAgain` was raised.

### CommandHandler

`CommandHandler` takes care of spawning receiver objects and initializing commands.
Handler is responsible for doing retries and forcing `undo` actions on commands.

### CommandMapper

`CommandMapepr` is a simple singleton.
It acts as a registry for command and ties together a command, command name, arguments and the receiver class.

## Interactions

Interaction is defined by two components - `IThread` and `InteractInterface`.

### IThread

`IThread` abstracts and separates communication threads from interfaces.
This allows for flows where one thread is spanning across different interfaces (imagine starting a command from the text interface and receiving the result over rest).

### InteractInterface

... or just interfaces.

Interfaces are initialised with command and result queues, so essentially they are bound to a command engine instance.
Each interface is called with `listen`, which is the method that is called to "start" the interface.
Interfaces should handle their operations in a thread safe manner.
Interfaces receive commands from users, which are added to their command queue and are kept within a local inventory.
Interfaces can post a message to a thread.
Interfaces can also post the result of a command. This method is called when a command is 'posting' it's results.


## Engines

Engines are dedicated to a functionality. They need to provide thread-safe handling of their functionality.
All engines are expected to handle objects they are dedicated to within two methods:

* `execute` - this method is the logic "engine"
* `run` - this method should take care that `execute` part of the engine is always running. `run` is the method that is called from the main thread.

At the moment kitchen aid supports two engines - `CommandEngine` and `InteractEngine`.

### CommandEngine

`CommandEngine` is tasked with loading commands, executing them and returning the results in async manner.
This class has two queues - one that contains the commands that are scheduled for execution and one that keeps the result and sends it to an interact module.

Valid commands that are read from the queue should be a tuple of the following form - command name, list of args, dict of args, thread that will be used for a response and interface over which response needs to happen.
Results are sent back to the interface in the form - command id, result.

For command id, check the `cmd_id` function within `interact.py` module.

### InteractEngine

Interact engine generates interact interfaces based configuration.
It then starts the `listener` method for each interact in parallel.
