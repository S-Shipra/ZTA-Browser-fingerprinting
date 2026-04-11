async function login() {

    const fingerprint = await getFingerprint();

    const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value,
            fingerprint: fingerprint
        })
    });

    const data = await response.json();

    // 🔥 STORE BREAKDOWN SAFELY
    if (data.risk_breakdown) {
        localStorage.setItem(
            "risk_breakdown",
            JSON.stringify(data.risk_breakdown)
        );
    }

    // 🔥 UI RESULT
    const resultBox = document.getElementById("result");

    resultBox.innerHTML =
        "Decision: " + data.decision + " | Risk: " + data.risk;

    // 🔥 SHOW BREAKDOWN ON LOGIN PAGE
    if (data.risk_breakdown) {

        let html = "<br><b>Risk Breakdown:</b><ul>";

        for (let key in data.risk_breakdown) {
            html += `<li>${key}: +${data.risk_breakdown[key]}</li>`;
        }

        html += "</ul>";

        resultBox.innerHTML += html;
    }

    // 🔐 OTP FLOW
    if (data.otp_required) {

        localStorage.setItem("user_id", data.user_id || 1);
        localStorage.setItem("otp_verified", "false");

        window.location.href = "otp.html";
        return;
    }

    // ✅ ALLOW FLOW
    if (data.decision === "ALLOW") {

        localStorage.setItem("otp_verified", "true");

        window.location.href = "dashboard.html";
    }
}