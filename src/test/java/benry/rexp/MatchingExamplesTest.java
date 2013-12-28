/**
 * $License: MIT License $
 */
package benry.rexp;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertNotNull;
import static org.hamcrest.CoreMatchers.is;

import static benry.rexp.Rexp.rexp;


@RunWith(JUnit4.class)
public class MatchingExamplesTest {

    @Test
    public void match__when_matched() {
        Matched m = rexp("^(\\d{4})-(\\d\\d)-(\\d\\d)$").match("2000-12-31");
        assertNotNull(m);
        assertThat(m.size(), is(3));
        assertThat(m.get(0), is("2000-12-31"));
        assertThat(m.get(1), is("2000"));
        assertThat(m.get(2), is("12"));
        assertThat(m.get(3), is("31"));
        //
        assertThat(m.start(1), is(0));
        assertThat(m.start(2), is(5));
        assertThat(m.start(3), is(8));
        //
        assertThat(m.end(1), is(4));
        assertThat(m.end(2), is(7));
        assertThat(m.end(3), is(10));
    }

    @Test
    public void match__when_not_matched() {
        Matched m = rexp("^(\\d{4})-(\\d\\d)-(\\d\\d)$").match("2000/12/31");
        assertNull(m);
    }

    @Test
    public void matchAll__when_matched() {
        int i = 0;
        String[] expected = new String[]{null, "2000", "12", "31"};
        for (Matched m: rexp("(\\d+)").matchAll("2000-12-31")) {
            i++;
            assertThat(m.get(1), is(expected[i]));
        }
    }

    @Test
    public void matchAll__when_not_matched() {
        int i = 0;
        for (Matched m: rexp("(\\d+)").matchAll("abc")) {
            i++;
        }
        assertThat(i, is(0));
    }

}
