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
