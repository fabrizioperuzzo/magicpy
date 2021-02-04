self.dateexcept = False

try:
    pingInfoFilePath = "./DB/" + self.stock + ".ftr"
    df_base1 = pd.read_feather(pingInfoFilePath, columns=None, use_threads=True)
    self.in_date = df_base1.iloc[-1].Date
    # put index as date back again
    df_base1.set_index('Date', inplace=True)

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(self.stock, "exception in creating the initial date because : ", e, exc_type, fname, exc_tb.tb_lineno)
    self.in_date = in_date
    self.dateexcept = True

# da yahoo recuper solo gli ultimi giorni mancanti
df_base2 = web.get_data_yahoo(self.stock, self.in_date, interval=interv).copy()

# se non ho un db da cui partire
if self.dateexcept == True: df_base = df_base2
# se invece sono partito da un db esistente
if self.dateexcept == False: df_base = pd.concat([df_base1, df_base2])

# feather works only with reset index
df_base3 = df_base.reset_index()
df_base3.to_feather(pingInfoFilePath)
