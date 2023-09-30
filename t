<style>
    /* Custom CSS to center the form */
    .center-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }

    body {
        background-color: #343a40;
    }
</style>

<div class="center-container">
    <div class="col-md-6">
        <div class="card text-white bg-dark">
            <div class="card-body">
                <h2 class="card-title text-center">Register</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" name="username" minlength="5"  class="form-control" id="username" placeholder="Enter your username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" name="email" class="form-control" id="email" placeholder="Enter your email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" minlength="6" name="password" class="form-control" id="password" placeholder="Enter your password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Register</button>
                </form>
                <p class="mt-3 text-center">Already have an account? <a href="/login">Login</a></p>
            </div>
        </div>
    </div>
</div>