from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Travel Bucket"
net_id = ["Martin Stoyanov: mas764"," Leo Liang: wl353"," Yagmur Dulger: yd333","Yash Mundra: ym267"," Zixiao Wang: zw579"]

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
