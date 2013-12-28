/**
 * $License: MIT License $
 */
package benry.rexp;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import static org.junit.Assert.assertThat;
import static org.hamcrest.CoreMatchers.is;

import static benry.rexp.Rexp.rexp;


@RunWith(JUnit4.class)
public class ReplacingExamplesTest {

    @Test
    public void gsub__replaces_all_with_string() {
        String actual = rexp("\\d+").gsub("2000-12-31", "X");
        assertThat(actual, is("X-X-X"));
        actual = rexp("\\d").gsub("2000-12-31", "X");
        assertThat(actual, is("XXXX-XX-XX"));
    }

    @Test
    public void gsub__replaces_all_with_callback() {
        String actual = rexp("(\\d+)").gsub("2000-12-31", new Replacer() {
            public String replace(Matched m) {
                int val = Integer.parseInt(m.get(1));
                return Integer.toString(val+1);
            }
        });
        assertThat(actual, is("2001-13-32"));
    }

    @Test
    public void gsub__replaces_all_with_backref() {
        String actual = rexp("(\\d+)").gsub("2000-12-31", "<$1>");
        assertThat(actual, is("<2000>-<12>-<31>"));
    }

    @Test
    public void sub__replaces_first_with_string() {
        String actual = rexp("(\\d+)").sub("2000-12-31", "X");
        assertThat(actual, is("X-12-31"));
    }

    @Test
    public void sub__replaces_first_with_callback() {
        String actual = rexp("(\\d+)").sub("2000-12-31", new Replacer() {
            public String replace(Matched m) {
                int val = Integer.parseInt(m.get(1));
                return Integer.toString(val+1);
            }
        });
        assertThat(actual, is("2001-12-31"));
    }

    @Test
    public void sub__replaces_first_N_items_with_callback() {
        Replacer repl = new Replacer() {
            public String replace(Matched m) {
                int val = Integer.parseInt(m.get(1));
                return Integer.toString(val+1);
            }
        };
        assertThat(rexp("(\\d+)").sub("2000-12-31", repl, 1), is("2001-12-31"));
        assertThat(rexp("(\\d+)").sub("2000-12-31", repl, 2), is("2001-13-31"));
        assertThat(rexp("(\\d+)").sub("2000-12-31", repl, 3), is("2001-13-32"));
    }

    @Test
    public void sub__replaces_first_with_backref() {
        String actual = rexp("(\\d+)").sub("2000-12-31", "<$1>");
        assertThat(actual, is("<2000>-12-31"));
    }

}
