const { exec } = require('child_process');

function killProcesses() {
    exec('tasklist | findstr /I "python electron undetected_chromedriver"', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error fetching task list: ${error.message}`);
            return;
        }

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return;
        }

        // Parse the output to get PIDs
        const lines = stdout.trim().split('\n');
        const pids = lines.map(line => {
            const parts = line.split(/\s+/);
            return parts[1]; // PID is the second element
        });

        // Kill each PID
        if (pids.length > 0) {
            pids.forEach(pid => {
                exec(`taskkill /PID ${pid} /F`, (killError, killStdout, killStderr) => {
                    if (killError) {
                        console.error(`Error killing PID ${pid}: ${killError.message}`);
                        return;
                    }
                    if (killStderr) {
                        console.error(`Error: ${killStderr}`);
                        return;
                    }
                    console.log(`Successfully killed PID ${pid}`);
                });
            });
        } else {
            console.log('No Python or Electron processes found.');
        }
    });
}

// Call the function
killProcesses();
