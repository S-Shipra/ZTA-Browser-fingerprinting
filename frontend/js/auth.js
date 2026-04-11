async function login() {

    const fingerprint = await getFingerprint();

    let response;
    try {
        response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                username: document.getElementById("username").value,
                password: document.getElementById("password").value,
                fingerprint: fingerprint
            })
        });
    } catch(e) {
        document.getElementById("result").innerText = "✗ Connection failed — is the backend running?";
        return;
    }

    let data;
    try {
        data = await response.json();
        console.log("FULL RESPONSE:", data);
    } catch(e) {
        document.getElementById("result").innerText = "✗ Invalid response from server";
        return;
    }

    // ❌ Handle 401 invalid credentials
    if (response.status === 401) {
        document.getElementById("result").innerText = data.message || "Invalid credentials";
        return;
    }

    const resultBox = document.getElementById("result");

    // 🔥 STORE BREAKDOWN
    if (data.risk_breakdown) {
        localStorage.setItem("risk_breakdown", JSON.stringify(data.risk_breakdown));
    }

    // 🔥 SHOW RESULT
    resultBox.innerHTML = `Decision: ${data.decision} | Risk Score: ${data.risk}/100`;

    // 🔥 SHOW BREAKDOWN
    if (data.risk_breakdown) {
        let html = "<br><b>Risk Breakdown:</b><ul>";
        for (let key in data.risk_breakdown) {
            html += `<li>${key.replace(/_/g, ' ')}: +${data.risk_breakdown[key]}</li>`;
        }
        html += "</ul>";
        resultBox.innerHTML += html;
    }

    // 🚨 ALERT
    if (data.alert) {
        resultBox.innerHTML += `<br><span style="color:#ff3b5c">🚨 Suspicious activity flagged!</span>`;
    }

    // 🔐 OTP FLOW
    if (data.otp_required) {
        if (!data.user_id) {
            resultBox.innerText = "Server error: no user_id returned";
            return;
        }
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("otp_verified", "false");
        setTimeout(() => { window.location.href = "otp.html"; }, 1000);
        return;
    }

    // ✅ ALLOW FLOW
    if (data.decision === "ALLOW") {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("otp_verified", "true");
        setTimeout(() => { window.location.href = "dashboard.html"; }, 1000);
        return;
    }

    // ❌ BLOCK FLOW
    if (data.decision === "BLOCK") {
        resultBox.innerHTML += `<br><span style="color:#ff3b5c">❌ Access Denied — Risk too high.</span>`;
    }
}