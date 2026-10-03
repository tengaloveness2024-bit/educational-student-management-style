// ================================
// LOGIN FORM VALIDATION
// ================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", function (event) {

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        if (username === "" || password === "") {
            alert("Please enter both username and password.");
            event.preventDefault();
        }
    });
}


// ================================
// STUDENT FORM VALIDATION
// ================================

function validateStudentForm() {

    const studentId = document.getElementById("student_id").value.trim();
    const fullName = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const program = document.getElementById("program").value;
    const marks = document.getElementById("marks").value;

    if (studentId === "") {
        alert("Please enter the student ID.");
        return false;
    }

    if (fullName === "") {
        alert("Please enter the student's full name.");
        return false;
    }

    if (email === "" || !email.includes("@")) {
        alert("Please enter a valid email address.");
        return false;
    }

    if (program === "") {
        alert("Please select a programme.");
        return false;
    }

    if (marks === "" || isNaN(marks)) {
        alert("Please enter valid marks.");
        return false;
    }

    if (Number(marks) < 0 || Number(marks) > 100) {
        alert("Marks must be between 0 and 100.");
        return false;
    }

    return true;
}


// ================================
// DELETE CONFIRMATION
// ================================

function confirmDelete() {

    return confirm(
        "Are you sure you want to delete this student record?"
    );
}
