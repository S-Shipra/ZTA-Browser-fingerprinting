let chartInstance = null;

// 🔥 DRAW CHART SAFE
function drawChart(breakdown) {

    const ctx = document.getElementById('riskChart');

    const labels = Object.keys(breakdown);
    const values = Object.values(breakdown);

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Risk Contribution',
                data: values,
            }]
        }
    });
}

// 🔥 COMPUTE BREAKDOWN FROM LOGS (IMPORTANT FIX)
function computeBreakdown(logs) {

    const breakdown = {
        LOW: 0,
        MEDIUM: 0,
        HIGH: 0
    };

    logs.forEach(log => {
        if (log.risk <= 30) breakdown.LOW++;
        else if (log.risk <= 70) breakdown.MEDIUM++;
        else breakdown.HIGH++;
    });

    return breakdown;
}
function getRiskExplanation(risk, decision) {
    const reasons = [];

    if (risk === 0)   reasons.push("✅ Fully trusted device, no anomalies");
    if (risk >= 100)  reasons.push("🔴 Completely unknown device + high anomaly");
    if (risk >= 80)   reasons.push("🔴 High fingerprint mismatch or ML anomaly");
    if (risk >= 50 && risk < 80) reasons.push("🟡 New or unverified device");
    if (risk === 20)  reasons.push("🟢 Known device, not yet trusted");

    if (decision.includes("BLOCK"))  reasons.push("❌ Access denied by policy");
    if (decision.includes("OTP"))    reasons.push("⚡ Step-up auth triggered");
    if (decision.includes("ALLOW"))  reasons.push("✅ Policy cleared");
    if (decision.includes("ALERT"))  reasons.push("🚨 Security alert raised");

    return reasons.join(" | ") || "ℹ️ Standard login";
}

async function loadLogs() {

    try {
        const response = await fetch("http://127.0.0.1:5000/logs");
        const data = await response.json();

        console.log("DATA RECEIVED:", data);

        const table = document.getElementById("logsTable");
        const alertBox = document.getElementById("alertBox");

        table.innerHTML = "";

        if (alertBox) alertBox.innerText = "";
        

        // 🔥 OTP STATUS
        const otpStatus = localStorage.getItem("otp_verified");

        if (otpStatus === "true" && alertBox) {
            alertBox.innerText = "✅ OTP VERIFIED - SECURE SESSION";
            alertBox.style.color = "green";
        }
        // 🔥 CHECK ML STATUS (GLOBAL)
        const mlDetected = data.some(log => log.ml_detected);

        const mlBox = document.getElementById("mlStatus");
        if (mlBox) {
            mlBox.innerHTML =
                mlDetected
                    ? "🤖 ML Anomalies Detected"
                    : "✅ No ML Threats";
        }

        // 🔥 RENDER TABLE
        data.forEach(log => {

            // ✅ FIXED ML MARKING (INSIDE LOOP)
            if (log.ml_detected) {
                log.action += " 🤖 ML ALERT";
            }

            let color = "white";

            if (log.action.includes("BLOCK")) {
                color = "#ff4d4d";
            } else if (log.action.includes("OTP")) {
                color = "#ffd633";
            } else if (log.action.includes("ALLOW")) {
                color = "#66ff66";
            }

            if (alertBox && log.action.includes("ALERT")) {
                alertBox.innerText = "🚨 Suspicious Activity Detected!";
                alertBox.style.color = "red";
            }

            const row = `
                <tr style="background-color:${color}">
                    <td>${log.user_id}</td>
                    <td>${log.action}</td>
                    <td>${log.risk}</td>
                    <td>${log.timestamp}</td>
                </tr>
            `;

            table.innerHTML += row;
        });

        // 🔥 RENDER TABLE
        data.forEach(log => {

            let color = "white";

            if (log.action.includes("BLOCK")) color = "#ff4d4d";
            else if (log.action.includes("OTP")) color = "#ffd633";
            else if (log.action.includes("ALLOW")) color = "#66ff66";

            if (alertBox && log.action.includes("ALERT")) {
                alertBox.innerText = "🚨 Suspicious Activity Detected!";
                alertBox.style.color = "red";
            }

            const row = `
                <tr style="background-color:${color}">
                    <td>${log.user_id}</td>
                    <td>${log.action}</td>
                    <td>${log.risk}</td>
                    <td>${log.timestamp}</td>
                </tr>
            `;

            table.innerHTML += row;
        });

        // 🔥 BREAKDOWN + CHART FROM LOGS (NOT localStorage)
        const breakdown = computeBreakdown(data);

        document.getElementById("riskBreakdown").innerHTML = `
            <li>LOW: ${breakdown.LOW}</li>
            <li>MEDIUM: ${breakdown.MEDIUM}</li>
            <li>HIGH: ${breakdown.HIGH}</li>
        `;

        drawChart(breakdown);

    } catch (err) {
        console.error("ERROR:", err);
    }
}

// run
loadLogs();
setInterval(loadLogs, 5000);