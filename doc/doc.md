# Defined in `cmd_line_bot.core.cmd_line_bot`

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


# Defined in `cmd_line_bot.core.clb_interface`
## CLBCmdLine
```python
class CLBCmdLine(metaclass=ABCMeta):
```

```python
@abstractmethod
def __init__(self,
             content: str,
             author: str) -> None:
```

```python
@abstractmethod
def get_info(self) -> str:
```

## CLBCmdLine_Msg

```python
class CLBCmdLine_Msg(CLBCmdLine):
```

```python
def __init__(self,
             content: str,
             author: str,
             channelname: str) -> None:
```

```python
def get_info(self) -> str:
```

## CLBCmdLine_DM

```python
class CLBCmdLine_DM(CLBCmdLine):
```

```python
def __init__(self,
             content: str,
             author: str) -> None:
```

```python
def get_info(self) -> str:
```

## CLBCmdLine_DM

```python
class CLBDummyCmdLine(CLBCmdLine):
```

```python
def __init__(self,
             content: str,
             author: str) -> None:
```

```python
def get_info(self) -> str:
    return "[dm from %s] %s" % (self.author, self.content)
```

## CLBTask

```python
class CLBTask(metaclass=ABCMeta):
```

```python
def __init__(self,
             text: Optional[str] = None,
             filename: Optional[str] = None,
             cmdline: Optional[CLBCmdLine] = None) -> None:
```

## CLBTask\_Msg

```python
class CLBTask_Msg(CLBTask):
```

```python
def __init__(self,
             channelname: str,
             text: Optional[str],
             filename: Optional[str] = None,
             cmdline: Optional[CLBCmdLine] = None) -> None:
```

## CLBTask\_Msg

```python
class CLBTask_DM(CLBTask):
```

```python
def __init__(self,
             username: str,
             text: Optional[str],
             filename: Optional[str] = None,
             cmdline: Optional[CLBCmdLine] = None) -> None:
```

## CLBTask\_Gathered

```python
class CLBTask_Gathered(CLBTask):
```

```python
def __init__(self,
             task_list: Optional[List[CLBTask]] = None) -> None:
```

## create\_reply\_task

```python
def create_reply_task(cmdline: CLBCmdLine,
                      text: Optional[str] = None,
                      filename: Optional[str] = None) -> CLBTask:
```

# Defined in `cmd_line_bot.core.clb_error`

## CLBError
```python
class CLBError(Exception):
```

```python
def __init__(self, error_msg: str) -> None:
```
