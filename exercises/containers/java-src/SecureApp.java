public class SecureApp {
    public static void main(String[] args) {
        System.out.println("🔒 Secure Java Application Running in Distroless Container");
        System.out.println("Container ID: " + System.getenv().getOrDefault("HOSTNAME", "unknown"));
        System.out.println("Java Version: " + System.getProperty("java.version"));
        System.out.println("Operating System: " + System.getProperty("os.name"));

        // Simple web server simulation
        System.out.println("Starting secure web service...");

        int count = 0;
        while (count < 10) {
            try {
                Thread.sleep(2000);
                count++;
                System.out.println("Health check " + count + "/10 - Service is healthy ✅");
            } catch (InterruptedException e) {
                System.err.println("Service interrupted");
                Thread.currentThread().interrupt();
                break;
            }
        }

        System.out.println("🔒 Secure Java Application completed successfully");
    }
}
