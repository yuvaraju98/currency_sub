from jchart import Chart


class LineChart(Chart):
    chart_type = 'line'

    def __init__(self, values):
        super(LineChart, self).__init__()
        self.value_array=values

    def get_labels(self, **kwargs):
        return list(self.value_array.keys())

    def get_datasets(self, **kwargs):
        dict_single=[]
        dict_points = {}
        dict_points['label'] = "Conversion rates"
        dict_points['data']=list(self.value_array.values())
        dict_single.append(dict_points)
        return dict_single
