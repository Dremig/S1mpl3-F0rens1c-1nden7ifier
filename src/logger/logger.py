class Logger:
    # 颜色代码
    COLORS = {
        'info': '\033[94m',     # blue
        'warning': '\033[93m',  # yellow
        'error': '\033[91m',    # red
        'success': '\033[92m',  # green
        'ask': '\033[95m',      # purple
        'end': '\033[0m'        # reset
    }
    
    @staticmethod
    def info(message):
        print(f"{Logger.COLORS['info']}[INFO]{Logger.COLORS['end']} {message}")
    
    @staticmethod
    def warning(message):
        print(f"{Logger.COLORS['warning']}[WARNING]{Logger.COLORS['end']} {message}")
    
    @staticmethod
    def error(message):
        print(f"{Logger.COLORS['error']}[ERROR]{Logger.COLORS['end']} {message}")
    
    @staticmethod
    def success(message):
        print(f"{Logger.COLORS['success']}[SUCCESS]{Logger.COLORS['end']} {message}")

    @staticmethod
    def ask(message):
        print(f"{Logger.COLORS['ask']}[ASK]{Logger.COLORS['end']} {message}", end = '')