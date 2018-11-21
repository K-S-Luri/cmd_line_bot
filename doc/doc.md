# classes in `cmd_line_bot.core.cmd_line_bot`

## CLBInputFrontEnd
```python
class CLBInputFrontEnd(metaclass=ABCMeta):
```

```python
@abstractmethod
def run(self, callback: Callable[[CLBCmdLine], None]) -> None:
```

```python
@abstractmethod
def kill(self) -> None:
```

## CLBOutputFrontEnd
```python
class CLBOutputFrontEnd(metaclass=ABCMeta):
```

```python
@abstractmethod
def send_msg(self,
             channelname: str,
             text: Optional[str],
             filename: Optional[str]) -> None:
```

```python
@abstractmethod
def send_dm(self,
            username: str,
            text: Optional[str],
            filename: Optional[str]) -> None:
```

```python
@abstractmethod
def kill(self) -> None:
```

## CLBBackEnd
```python
class CLBBackEnd(metaclass=ABCMeta):
```

```python
@abstractmethod
def manage_cmdline(self,
                   cmdline: CLBCmdLine,
                   send_task: Callable[[CLBTask], None]) -> None:
```

```python
@abstractmethod
def kill(self) -> None:
```

## CmdLineBot
```python
class CmdLineBot:
```

```python
def __init__(self,
             input_frontend: Union[CLBInputFrontEnd, List[CLBInputFrontEnd]],
             output_frontend: CLBOutputFrontEnd,
             backend: CLBBackEnd) -> None:
```

```python
def run(self) -> None:
```
