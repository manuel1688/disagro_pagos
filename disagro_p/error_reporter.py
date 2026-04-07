import traceback

class ErrorReporter:
    def __init__(self,err_tuble):
        self.error_info = err_tuble
    
    def print_error_info(self):
        traceback.print_exception(self.error_info[0], self.error_info[1], self.error_info[2])

    def filename(self):
        return self.error_info[2].tb_frame.f_code.co_filename
    
    def line_number(self):
        return self.error_info[2].tb_lineno
