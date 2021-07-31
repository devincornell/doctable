

class WorkerResourceBaseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)

class WorkerDiedError(WorkerResourceBaseException):
    message = f'Worker died before finishing.'

class WorkerIsDeadError(WorkerResourceBaseException):
    message = f'Worker is already closed.'

class WorkerIsAliveError(WorkerResourceBaseException):
    message = f'Cannot start worker because it is already alive.'

class UnidentifiedMessageReceivedError(WorkerResourceBaseException):
    message = f'Worker received an invalid message.'

class WorkerResourceReceivedUnidentifiedMessage(WorkerResourceBaseException):
    message = 'This WorkerResource received an unidentified message.'

class WorkerHasNoUserFunctionError(WorkerResourceBaseException):
    message = (f'Worker was not provided with a function. '
            'Either provide a function when the worker is created '
            'or update the worker\'s function using '
            '.update_userfunc().')


#no_function_error_msg = ('Worker {pid} was not provided '
#    'with a function. Either provide a function when '
#    'the worker is created or send a NewFunction via '
#    'the pipe.')

