# class methods

## CLBInputFrontEnd
```python
class cmd_line_bot.core.cmd_line_bot.CLBInputFrontEnd(metaclass=ABCMeta):
```

### run

```python
@abstractmethod
def run(self, callback: Callable[[CLBCmdLine], None]) -> None:
```

### kill
```python
@abstractmethod
def kill(self) -> None:
```

## CLBOutputFrontEnd
```python
class CLBOutputFrontEnd(metaclass=ABCMeta):
```

### `send_msg`
```python
@abstractmethod
def send_msg(self,
             channelname: str,
             text: Optional[str],
             filename: Optional[str]) -> None:
```
