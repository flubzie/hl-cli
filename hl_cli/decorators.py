import argparse

def command_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SystemExit: # allows continuing the interactive shell when options like --help are used
            pass
        except argparse.ArgumentError as e:
            print('Error:', e)
        except Exception as e:
            if 'ConnectionResetError' in str(e):
                for i in range(5):
                    print(f'Error: Connection reset by peer, retrying({i})...')
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        pass
            print('Error:', e)
    return wrapper
