import datetime
import time


class Options:

    def __init__(self, MongoCrud, Chart):
        self.MongoCrud = MongoCrud
        self.Chart = Chart

        self.IMAGE_PREFIX = "img:"
        self.date_format = "%Y-%m-%d"

    def answer_message(self, fb_id, message):
        try:
            print("Options.answer_message", fb_id, message)
            args = message.strip().split(" ")
            if args[0].lower() == "register":
                return [
                    self.register(
                        facebook_id=fb_id,
                        actual_value=args[1],
                        end_value=args[3],
                        end_time=self.parse_date(args[2])
                    )
                ]
            if args[0].lower() == "stat":
                return [
                    self.stat(fb_id),
                    self.IMAGE_PREFIX + self.Chart.stat_pic(fb_id)
                ]
            if self.is_float(args[0].replace(",", ".")):
                return [
                    self.save_actual_weight(fb_id, float(args[0])),
                    self.stat(fb_id),
                    self.IMAGE_PREFIX + self.Chart.stat_pic(fb_id)
                ]

            return [self.help_msg()]
        except:
            return [self.help_msg()]

    def help_msg(self):
        return """
        version: 0.1.7
        
        examples:
        - Register 100 2018-06-01 90
          (register <actual weight> <plan end date> <planned weight>)
        - 89.9
          (a float input, represents the actual weight)
        - Stat
          (tell you the actual expected value for the progress)
        """

    def parse_date(self, d):
        return round(time.mktime(datetime.datetime.strptime(d, self.date_format).timetuple()))

    def save_actual_weight(self, fb_id, weight):
        self.MongoCrud.save_progress(fb_id, self.actual_timestamp(), weight)
        return "OK, you are {} kg today".format(weight)

    def stat(self, fb_id):
        ts_now = self.actual_timestamp()
        plan = self.MongoCrud.registered_plan_in_mongo(fb_id)
        val_actual = self.MongoCrud.planned_values(fb_id, ts_now, plan)
        return "your planned weigth for today is: {} kg".format(val_actual)

    def register(self, facebook_id, actual_value, end_time, end_value):
        self.MongoCrud.register_plan_in_mongo(facebook_id, self.actual_timestamp(), end_time, float(actual_value),
                                              float(end_value))
        return "Your plan has been registered"

    @staticmethod
    def actual_timestamp():
        return round(time.time())

    @staticmethod
    def is_float(f):
        try:
            float(f)
            return True
        except:
            return False