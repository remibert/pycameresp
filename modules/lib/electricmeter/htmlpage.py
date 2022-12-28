page = b"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
<canvas id="line-chart"></canvas>
<span id="legend"></span>
<script>
var STEP         = %d;
var DAY_SELECTED = '%s';
var DATE         = '%s';
var CHART_TYPE   = '%s';
var chart   = null;

function pad(num, size) 
{
	num = parseInt(num);
	num = num.toString();
	while (num.length < size) 
	{
		num = "0" + num;
	}
	return num;
}

function capitalize(string) 
{
	return string.charAt(0).toUpperCase() + string.slice(1);
}

class Cost
{
	constructor(name, currency, color)
	{
		this.total_cost   = 0;
		this.total_pulses = 0;
		this.currency = currency;
		this.name  = name;
		this.color = color;
		this.pulses = [];
		this.costs  = [];
	}
}

class Costs
{
	constructor(datas)
	{
		this.costs = new Map();
		this.datas = datas;
		this.labels = [];
		this.step_pulses = 0;
		for (let i = 0; i < this.datas.rates.length; i++)
		{
			var rate = this.datas.rates[i];
			if (!this.costs.has(rate.rate))
			{
				this.costs.set(rate.rate, new Cost(rate.rate, rate.currency, rate.color));
			}
		}
	}
		
	add_step(minute, pulses)
	{
		var rate = null;
		minute *= 60;
		for (let i = 0; i < this.datas.rates.length; i++)
		{
			rate = this.datas.rates[i];
			if (minute >= rate.start_time && minute <= rate.end_time)
			{
				rate = this.datas.rates[i];
				break;
			}
		}
		
		for (var [name, cost] of this.costs)
		{
			if (cost.name === rate.rate)
			{
				var current_cost = (rate.price / 1000.) * pulses
				if (STEP <= 15)
				{
					cost.pulses.push(pulses);
				}
				else
				{
					cost.pulses.push((pulses/1000.).toFixed(2));
				}
				cost.costs.push(current_cost.toFixed(2));
				cost.total_cost   += current_cost;
				cost.total_pulses += pulses;
			}
			else
			{
				cost.pulses.push(0);
				cost.costs.push(0);
			}
		}
	}

	parse_step(minute, pulses)
	{
		this.step_pulses += pulses;
		if ((minute + 1)%%STEP == 0)
		{
			var time = pad((minute+1)/60, 2) + ":" + pad((minute+1)%%60, 2);
			this.labels.push(time);
			this.add_step(minute, this.step_pulses);
			this.step_pulses = 0;
		}
	}
	
	parse()
	{
		for (let minute = 0; minute < this.datas.pulses.length; minute++)
		{
			this.parse_step(minute, this.datas.pulses[minute]);
		}
	}
	
	get_data_set()
	{
		var result = [];
		var data = null;
		var unit = "";
		for (var [name, cost] of this.costs)
		{
			if (CHART_TYPE === "price")
			{
				unit = cost.currency;
				data = cost.costs;
			}
			else
			{
				if (STEP <= 15)
				{
					unit = "Wh";
				}
				else
				{
					unit = "kWh";
				}
				data = cost.pulses;
			}
			result.push(
				{ 
					data: data,
					label: cost.name + " (" + unit + ")",
					backgroundColor: cost.color,
					fill: false,
					pointRadius:1,
					borderWidth:0
				});
			
		}
		
		return result;
	}
	
	get_labels()
	{
		return this.labels;
	}
	
	get_legend()
	{
		var legend = "<br>";
		var result = capitalize(DATE) + ' : ';
		var total = 0;
		var currency = "";
		if (CHART_TYPE === "price")
		{
			for (var [name, cost] of this.costs)
			{
				total += cost.total_cost;
				currency = cost.currency;
				legend += "<li>" + cost.name  + " : " + cost.total_cost.toFixed(2) + " " + cost.currency + "</li>";
			}
			result += total.toFixed(2) + currency;
		}
		else
		{
			for (var [name, cost] of this.costs)
			{
				total += cost.total_pulses;
				legend += "<li>" + cost.name  + " : " + (cost.total_pulses / 1000).toFixed(2) + " kWh </li>";
			}
			result += (total/1000).toFixed(2) + " kWh";
		}
		document.getElementById("legend").innerHTML="<ul>" + capitalize(legend) + "</ul>";
		return result;
	}
}


function show_chart(datas)
{
	var costs = new Costs(datas);
	
	costs.parse();
	if (!(chart === null))
	{
		chart.destroy();
		chart = null;
	}
	costs.get_legend();
	chart = new Chart(document.getElementById("line-chart"), 
	{
		type: 'bar',
		data: 
		{
			labels: costs.get_labels(),
			datasets: costs.get_data_set()
		},
		options: 
		{
			responsive: true,
			animation:
			{
				duration: 0
			},
			plugins:
			{
				legend:
				{
					position: 'top',
				},
				title:
				{
					display: true,
					text: costs.get_legend()
				}
			},
			scales:
			{
				x:
				{
					stacked: true,
				}
			}
		}
	});
}

async function download_datas()
{
	const response = await fetch('/pulses_rates?day='+DAY_SELECTED);
	var data = await response.json();
	show_chart(data);
}

download_datas();

const d = new Date();
var currentDate = d.getFullYear() + "-" + pad(d.getMonth()+1,2) + "-" + pad(d.getDate(),2);
if (DAY_SELECTED === currentDate)
{
	setInterval(download_datas, 5000);
}
</script>
"""