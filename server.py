from threading import Thread
from os import environ
from typing import AnyStr, AsyncIterable, ByteString, ValuesView, List, MappingView, OrderedDict, DefaultDict, ContextManager, Union, Optional, \
    ItemsView, Callable, ClassVar, Type, Pattern, NoReturn, AsyncGenerator, Match, Set, Dict, MutableSequence, Generator, Counter, Collection, \
    Sized, AsyncContextManager, Tuple, Sequence, Deque, Reversible, AbstractSet, Final, Iterator, Mapping, AsyncIterator, Container, MutableSet, \
    Literal, ChainMap, KeysView, Any, MutableMapping, Iterable, Coroutine, FrozenSet, Awaitable, Hashable

from flask import Flask, request

from smartpool import SmartPool


class ReturnValContainer:
    def __init__(self):
        self.value = None


def exec_and_return(payload: str, _globals={}):
    exec(payload, _globals)
    return _globals["return_value_container"].value


exec_globals = {
    "return_value_container": ReturnValContainer(),
    "AnyStr": AnyStr,
    "AsyncIterable": AsyncIterable,
    "ByteString": ByteString,
    "ValuesView": ValuesView,
    "List": List,
    "MappingView": MappingView,
    "OrderedDict": OrderedDict,
    "DefaultDict": DefaultDict,
    "ContextManager": ContextManager,
    "Union": Union,
    "Optional": Optional,
    "ItemsView": ItemsView,
    "Callable": Callable,
    "ClassVar": ClassVar,
    "Type": Type,
    "Pattern": Pattern,
    "NoReturn": NoReturn,
    "AsyncGenerator": AsyncGenerator,
    "Match": Match,
    "Set": Set,
    "Dict": Dict,
    "MutableSequence": MutableSequence,
    "Generator": Generator,
    "Counter": Counter,
    "Collection": Collection,
    "Sized": Sized,
    "AsyncContextManager": AsyncContextManager,
    "Tuple": Tuple,
    "Sequence": Sequence,
    "Deque": Deque,
    "Reversible": Reversible,
    "AbstractSet": AbstractSet,
    "Final": Final,
    "Iterator": Iterator,
    "Mapping": Mapping,
    "AsyncIterator": AsyncIterator,
    "Container": Container,
    "MutableSet": MutableSet,
    "Literal": Literal,
    "ChainMap": ChainMap,
    "KeysView": KeysView,
    "Any": Any,
    "MutableMapping": MutableMapping,
    "Iterable": Iterable,
    "Coroutine": Coroutine,
    "FrozenSet": FrozenSet,
    "Awaitable": Awaitable,
    "Hashable": Hashable
}


pool = SmartPool(
    worker_fn=exec_and_return,
    kwargs={"_globals": exec_globals},
    num_workers=int(environ["PYRUNNER_NUM_WORKERS"]),
    timeout_sec=float(environ["PYRUNNER_TIMEOUT_SEC"]),
    maxmem_bytes=int(environ["PYRUNNER_MAXMEM_MB"])*1024*1024)
app = Flask(__name__)


@app.get("/Config")
def get_server_params():
    return {
        "num_workers": int(environ["PYRUNNER_NUM_WORKERS"]),
        "timeout_sec": float(environ["PYRUNNER_TIMEOUT_SEC"]),
        "maxmem_mb": int(environ["PYRUNNER_MAXMEM_MB"])}


@app.get("/")
def get_result():
    num_results = request.json["num_results"]
    results = []
    while pool.result_ready() and len(results) < num_results:
        # pool.result_ready() does not guarantee an item is actually there for us to grab
        # in this case, pool.get_result() will just return None
        result = pool.get_result()
        if result is None:
            break
        return_val = result.return_val.__repr__() if isinstance(result.return_val, Exception) else result.return_val
        results.append({"id": result.id, "returned": return_val})
    return results


@app.post("/")
def post_request():
    try:
        for job in request.json:
            pool.put_job(job["id"], job["src_code"])
    except Exception as e:
        return e.__repr__()
    return "OK"


if __name__ == "__main__":
    smartpool_thread = Thread(target=pool, name='smartpool_thread', daemon=True)
    smartpool_thread.start()
    app.run(host="0.0.0.0", port=int(environ["PYRUNNER_PORT"]))
