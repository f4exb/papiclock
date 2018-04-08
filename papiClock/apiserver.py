#!/usr/bin/env python
import web, json

meteo_dict = {
    "update_ts" : 0,
    "run_number": 0,
    "geoloc" : {
        "lat": 0,
        "lon": 0
    },
    "data": {}
}

urls = (
    '/api/meteo', 'web_process_meteo',
    '/api/meteo/run', 'web_process_run'
)

class MyApp(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

app = MyApp(urls, globals())

class web_process_meteo:
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        output = json.dumps(meteo_dict)
        return output

class web_process_run:
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        meteo_run_dict = {}
        meteo_run_dict["update_ts"] = meteo_dict["update_ts"]
        meteo_run_dict["run_number"] = meteo_dict["run_number"]
        meteo_run_dict["geoloc"] = {}
        meteo_run_dict["geoloc"]["lat"] = meteo_dict["geoloc"]["lat"]
        meteo_run_dict["geoloc"]["lon"] = meteo_dict["geoloc"]["lon"]
        output = json.dumps(meteo_run_dict)
        return output

def run(port = 8080):
    app.run(port=port)

def stop():
    app.stop()
