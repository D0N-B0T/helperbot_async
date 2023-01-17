import structlog
log = structlog.get_logger()

def SomeClass(x, y):
    log.info("SomeClass", x=x, y=y)
    return x + y

def make_call_stack_more_impressive():
    try:
        d = {"x":42}
        print(SomeClass(d["y"], "foo"))
    except Exception:
        log.exception(f"poor me")
    log.info("done", stack_info=True)

SomeClass(1, 2)
make_call_stack_more_impressive()
        