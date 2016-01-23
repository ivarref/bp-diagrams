package no.ivarref;

import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import org.apache.commons.io.FileUtils;
import org.eclipse.jetty.server.Request;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.AbstractHandler;
import org.eclipse.jetty.server.handler.HandlerList;
import org.eclipse.jetty.server.handler.ResourceHandler;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.Arrays;
import java.util.TreeSet;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class PngServer {

    final static boolean isDocker = new File("/bp-diagrams").exists();

    final static Object lock = new Object();
    final RemoteWebDriver driver;
    final String selfIp;

    final LoadingCache<String, ByteContainer> pngCache = CacheBuilder.newBuilder()
            .maximumSize(10000)
            .build(new CacheLoader<String, ByteContainer>() {
                public ByteContainer load(String key) throws Exception {
                    return generatePng(key);
                }
            });

    public PngServer(RemoteWebDriver driver, String selfIp) {
        this.driver = driver;
        this.selfIp = selfIp;
    }

    public static void main(String[] args) throws Exception {
        String selfIp = Arrays.asList(args)
                .stream()
                .filter(s -> s.startsWith("-DselfIp="))
                .map(s -> s.split("=")[1])
                .findFirst().orElse("localhost");

        RemoteWebDriver driver = isDocker ? new RemoteWebDriver(new URL("http://phantomjs:8910"), DesiredCapabilities.phantomjs()) : new FirefoxDriver();
        new PngServer(driver, selfIp).run();
    }

    public void run() throws Exception {
        System.out.println("starting webserver with selfIp = " + selfIp + ", isDocker = " + isDocker);
        Server server = new Server(8080);

        if (isDocker) {
            setupSafeWebHosting();
        }

        server.setHandler(new HandlerList() {{
            addHandler(generatePNGHandler(driver, selfIp));
            addHandler(new ResourceHandler() {{
                setResourceBase(isDocker ? "/bp-diagrams/target/web" : ".");
            }});
        }});

        server.start();
        server.join();
    }

    private static void setupSafeWebHosting() throws IOException {
        for (String s : Arrays.asList("data/data.tsv", "d3.v3.min.js", "index.html")) {
            FileUtils.copyFile(new File("/bp-diagrams/" + s), new File("/bp-diagrams/target/web/" + s));
        }
    }

    private AbstractHandler generatePNGHandler(final RemoteWebDriver driver, final String selfIp) {
        AtomicLong counter = new AtomicLong(0);
        return new AbstractHandler() {
            @Override
            public void handle(String p, Request request, HttpServletRequest httpServletRequest, HttpServletResponse response) throws IOException, ServletException {
                logRequest(request, counter);
                boolean isDownload = request.getParameter("dl") != null;
                boolean generateImage = isDownload || "t".equalsIgnoreCase(request.getParameter("i"));
                if (generateImage) {
                    servePNGImage(request, response, isDownload);
                }
            }
        };
    }

    private void servePNGImage(Request request, HttpServletResponse response, boolean isDownload) throws IOException {
        request.setHandled(true);
        String url = getSafeURL(request);

        try {
            byte[] screenShot = isDocker ? pngCache.get(url).png : generatePng(url).png;
            if (isDownload) {
                response.setContentType("application/x-download");
                response.setHeader("Content-Disposition", "attachment; filename=" + downloadFileName(request));
            } else {
                response.setContentType("image/png");
            }
            response.setContentLength(screenShot.length);
            response.getOutputStream().write(screenShot);
            response.setStatus(200);
        } catch (ExecutionException e) {
            e.printStackTrace();
            System.err.println("error generating PNG for: " + url);
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        }
    }

    private String downloadFileName(Request request) {
        return String.join("_", new TreeSet<>(request.getParameterMap().keySet())
                .stream()
                .filter(s -> s.matches("^[a-zA-Z_]+$") && !("dl".equalsIgnoreCase(s) || "i".equalsIgnoreCase(s)) && request.getParameter(s).matches("^[a-zA-Z0-9_,]+$"))
                .map(s -> request.getParameter(s).replace(",", "_"))
                .collect(Collectors.toList())) + ".png";
    }

    private static String getSafeURL(Request request) {
        String url = String.join("&", new TreeSet<>(request.getParameterMap().keySet())
                .stream()
                .filter(s -> s.matches("^[a-zA-Z_]+$") && !("dl".equalsIgnoreCase(s) || "i".equalsIgnoreCase(s) || "image".equalsIgnoreCase(s)) && request.getParameter(s).matches("^[a-zA-Z0-9_,]+$"))
                .map(s -> s + "=" + request.getParameter(s))
                .collect(Collectors.toList()));

        url += "&printer=true";
        return url;
    }

    public ByteContainer generatePng(String key) {
        synchronized (lock) {
            long start = System.currentTimeMillis();
            driver.get("http://" + selfIp + ":8080/?" + key);
            byte[] screenShot = driver.getScreenshotAs(OutputType.BYTES);
            long diff = System.currentTimeMillis() - start;
            System.out.println("time to take screenshot: " + diff + " ms, length of screenshot: " + screenShot.length + ", url: " + key);
            return new ByteContainer(screenShot);
        }
    }

    private static void logRequest(Request request, AtomicLong counter) {
        System.out.println("req :: " + counter.incrementAndGet() + " " + request.getRequestURI() + "?" +
                String.join("&", new TreeSet<>(request.getParameterMap().keySet())
                        .stream()
                        .map(s -> s + "=" + request.getParameter(s))
                        .collect(Collectors.toList())
                ));
    }

    public static class ByteContainer {
        public final byte[] png;

        public ByteContainer(byte[] png) {
            this.png = png;
        }
    }
}
