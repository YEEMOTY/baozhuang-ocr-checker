def execute_after_n_calls(n, w2set):
    def decorator(func):
        def wrapper(*args, **kwargs):
            wrapper.count += 1
            result = func(*args, **kwargs)
            if wrapper.count % n == 0:
                w2set()
            return result
        wrapper.count = 0
        return wrapper
    return decorator

def bb():
    print('b')

@execute_after_n_calls(3, bb)
def aa():
    print('a')


aa()
aa()
aa()
aa()
aa()
aa()
