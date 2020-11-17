//line
var ctxL = document.getElementById("lineChart").getContext('2d');

var epc_count = epcExpiryCount;
var tm44_count = tm44ExpiryCount;
var dec_count = decExpiryCount;

var myLineChart = new Chart(ctxL, {
	type: 'line',
	data: {
		labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
		datasets: [
			{
				label: "EPCs",
				data: epc_count,
				backgroundColor: ['rgba(35, 155, 86, .2)',],
				borderColor: ['rgba(24, 104, 58, .7)',],
				borderWidth: 2
			},
			{
				label: "TM44s",
				data: tm44_count,
				backgroundColor: ['rgba(66, 139, 202, .2)',],
				borderColor: ['rgba(32, 78, 118, .7)',],
				borderWidth: 2
			},
			{
				label: "DECs",
				data: dec_count,
				backgroundColor: ['rgba(236, 112, 99, .2)',],
				borderColor: ['rgba(176, 49, 35, .7)',],
				borderWidth: 2
			}
		]
	},
	options: {
		responsive: true
	}
});

var ctx = document.getElementById("barChart").getContext('2d');
var epcCount = epcCount
console.log(epcCount)
var tm44Count = tm44Count
console.log(tm44Count)
var decCount = decCount
console.log(decCount)

var myBarChart = new Chart(ctx, {
	type: 'bar',
	data: {
		datasets: [
			{
				data: [epcCount],
				label: 'EPCs',
				barPercentage: 0.5,
		        barThickness: 6,
		        maxBarThickness: 8,
		        minBarLength: 2,
		        backgroundColor: ['rgba(35, 155, 86, .2)',],
				borderColor: ['rgba(24, 104, 58, .7)',],
				borderWidth: 2
			},
			{
				data: [tm44Count],
				label: 'TM44s',
				barPercentage: 0.5,
		        barThickness: 6,
		        maxBarThickness: 8,
		        minBarLength: 2,
				backgroundColor: ['rgba(66, 139, 202, .2)',],
				borderColor: ['rgba(32, 78, 118, .7)',],
				borderWidth: 2
			},
			{
				data: [decCount],
				label: 'DECs',
				barPercentage: 0.5,
		        barThickness: 6,
		        maxBarThickness: 8,
		        minBarLength: 2,
		        backgroundColor: ['rgba(236, 112, 99, .2)',],
				borderColor: ['rgba(176, 49, 35, .7)',],
				borderWidth: 2
			}
		]
	},
	// options: {
	// 	responsive: true
	// }
});