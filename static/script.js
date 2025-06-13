function resetbutton(){
    fetch("/resetbutton", { method: "POST" })
}
function updateLiveVisitorTable() {
    fetch('/api/live_visitors')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("visitor-table-body");
            tbody.innerHTML = "";

            data.forEach(visitor => {
                const timeExit = visitor.timeexit ? visitor.timeexit : '---';
                const photo = visitor.photo ? `<img src="data:image/jpeg;base64,${visitor.photo}" alt="photo" width="60" height="60" class="rounded-circle">` : 'N/A';

                tbody.innerHTML += `
                    <tr>
                        <td>${visitor.id}</td>
                        <td>${photo}</td>
                        <td>${visitor.name} ${visitor.lastname}</td>
                        <td>${visitor.phone}</td>
                        <td>${visitor.company}</td>
                        <td>${visitor.timeentry}</td>
                        <td>${timeExit}</td>
                        <td>
                            <form action="/mark_exit/${visitor.id}" method="POST">
                                <button type="submit" class="btn btn-danger btn-sm">Mark Exit</button>
                            </form>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => {
            console.error('Error fetching visitor data:', error);
        });
}

// Auto-refresh every 5 seconds
setInterval(updateLiveVisitorTable, 5000);
window.onload = updateLiveVisitorTable;
