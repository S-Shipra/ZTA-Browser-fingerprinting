// 🔐 HMAC GENERATION
async function generateHMAC(data) {
    const enc = new TextEncoder();
    const key = "super_secret_key_123";  // must match backend SECRET_KEY

    const cryptoKey = await crypto.subtle.importKey(
        "raw",
        enc.encode(key),
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign"]
    );

    const signature = await crypto.subtle.sign(
        "HMAC",
        cryptoKey,
        enc.encode(JSON.stringify(data))
    );

    return Array.from(new Uint8Array(signature))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}


// 🔐 LOGIN FUNCTION
async function login() {

    const fingerprint = await getFingerprint();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // 🔴 ADD TIMESTAMP + SIGNATURE
    const timestamp = Date.now();

    const signature = await generateHMAC({
        fingerprint,
        timestamp
    });

    let response;

    try {
        response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password,
                fingerprint,
                timestamp,
                signature
            })
        });
    } catch (e) {
        document.getElementById("result").innerText =
            "✗ Connection failed — is the backend running?";
        return;
    }

    let data;
    try {
        data = await response.json();
        console.log("FULL RESPONSE:", data);
    } catch (e) {
        document.getElementById("result").innerText =
            "✗ Invalid response from server";
        return;
    }

    // ❌ Invalid credentials
    if (response.status === 401) {
        document.getElementById("result").innerText =
            data.message || "Invalid credentials";
        return;
    }

    const resultBox = document.getElementById("result");

    // 🔥 STORE JWT TOKEN
    if (data.token) {
        localStorage.setItem("token", data.token);
    }

    // 🔥 STORE BREAKDOWN (if backend sends it)
    if (data.risk_breakdown) {
        localStorage.setItem(
            "risk_breakdown",
            JSON.stringify(data.risk_breakdown)
        );
    }

    // 🔥 SHOW RESULT
    resultBox.innerHTML =
        `Decision: ${data.decision} | Risk Score: ${data.risk}/100`;

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
        resultBox.innerHTML +=
            `<br><span style="color:#ff3b5c">🚨 Suspicious activity flagged!</span>`;
    }

    // 🔐 OTP FLOW
    if (data.otp_required) {
        if (!data.user_id) {
            resultBox.innerText = "Server error: no user_id returned";
            return;
        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("otp_verified", "false");

        setTimeout(() => {
            window.location.href = "otp.html";
        }, 1000);

        return;
    }

    // ✅ ALLOW FLOW
    if (data.decision === "ALLOW") {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("otp_verified", "true");

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1000);

        return;
    }

    // ❌ BLOCK FLOW
    if (data.decision === "BLOCK") {
        resultBox.innerHTML +=
            `<br><span style="color:#ff3b5c">❌ Access Denied — Risk too high.</span>`;
    }
}