async function verifyOTP() {

    const user_id = localStorage.getItem("user_id");

    const response = await fetch("http://127.0.0.1:5000/verify-otp", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: user_id,
            otp: document.getElementById("otp").value
        })
    });

    const data = await response.json();

    document.getElementById("result").innerText = data.message;

    if (data.status === "ALLOW") {

        localStorage.setItem("otp_verified", "true");

        window.location.href = "dashboard.html";
    }
}