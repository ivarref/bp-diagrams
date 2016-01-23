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
import java.util.stream.Collectors;

public class PngServer {

    final static Object lock = new Object();

    public static void main(String[] args) throws Exception {
        String selfIp = Arrays.asList(args)
                .stream()
                .filter(s -> s.startsWith("-DselfIp="))
                .map(s -> s.split("=")[1])
                .findFirst().orElse("localhost");

        Server server = new Server(8080);
        boolean isDocker = new File("/bp-diagrams").exists();
        System.out.println("starting webserver with selfIp = " + selfIp + ", isDocker = " + isDocker);

        if (isDocker) {
            for (String s : Arrays.asList("data/data.tsv", "d3.v3.min.js", "index.html")) {
                FileUtils.copyFile(new File("/bp-diagrams/" + s), new File("/bp-diagrams/target/web/" + s));
            }
        }

        RemoteWebDriver driver = isDocker ? new RemoteWebDriver(new URL("http://phantomjs:8910"), DesiredCapabilities.phantomjs()) : new FirefoxDriver();

        server.setHandler(new HandlerList() {{
                addHandler(generatePNGHandler(driver, selfIp));
                addHandler(new ResourceHandler() {{ setResourceBase(isDocker ? "/bp-diagrams/target/web" : "."); }});
        }});

        server.start();
        server.join();
    }

    private static AbstractHandler generatePNGHandler(final RemoteWebDriver driver, final String selfIp) {
        LoadingCache<String, ByteContainer> pngCache = CacheBuilder.newBuilder()
                .maximumSize(10000)
                .build(new CacheLoader<String, ByteContainer>() {
                            public ByteContainer load(String key) throws Exception {
                                synchronized (lock) {
                                    long start = System.currentTimeMillis();
                                    driver.get("http://" + selfIp + ":8080/?" + key);
                                    byte[] screenShot = driver.getScreenshotAs(OutputType.BYTES);
                                    long diff = System.currentTimeMillis() - start;
                                    System.out.println("time to take screenshot: " + diff + " ms, length of screenshot: " + screenShot.length + ", url: " + key);
                                    return new ByteContainer(screenShot);
                                }
                            }
                        });

        return new AbstractHandler() {
            @Override
            public void handle(String p, Request request, HttpServletRequest httpServletRequest, HttpServletResponse response) throws IOException, ServletException {
                if ("true".equalsIgnoreCase(request.getParameter("image"))) {
                    request.setHandled(true);
                    String url = String.join("&", new TreeSet<>(request.getParameterMap().keySet())
                            .stream()
                            .filter(s -> s.matches("^[a-zA-Z_]+$") && !("image".equalsIgnoreCase(s)) && request.getParameter(s).matches("^[a-zA-Z0-9_,]+$"))
                            .map(s -> s + "=" + request.getParameter(s))
                            .collect(Collectors.toList()));

                    try {
                        byte[] screenShot = pngCache.get(url).png;
                        response.setContentType("image/png");
                        response.setContentLength(screenShot.length);
                        response.getOutputStream().write(screenShot);
                        response.setStatus(200);
                    } catch (ExecutionException e) {
                        e.printStackTrace();
                        System.err.println("error generating PNG for: " + url);
                        response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                    }
                }
            }
        };
    }

    public static class ByteContainer {
        public final byte[] png;

        public ByteContainer(byte[] png) {
            this.png = png;
        }
    }
}
