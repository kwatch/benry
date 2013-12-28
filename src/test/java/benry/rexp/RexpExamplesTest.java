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
import static org.junit.Assert.assertSame;
import static org.junit.Assert.assertNotSame;
import static org.hamcrest.CoreMatchers.is;

import benry.rexp.Rexp;
import static benry.rexp.Rexp.rexp;


@RunWith(JUnit4.class)
public class RexpExamplesTest {

    @Test
    public void rexp__returns_Rexp_object() {
        Rexp rx1 = rexp("^\\d$");
        assertThat(rx1, is(Rexp.class));
        Rexp rx2 = rexp("^\\.(jpg|png|gif)$", "i");
        assertThat(rx2, is(Rexp.class));
    }

    @Test
    public void rexp__caches_compiled_result() {
        assertSame(rexp("\\d"), rexp("\\d"));
        assertNotSame(rexp("\\d"), rexp("\\d", "i"));
    }

    @Test
    public void Rexp__not_cache_compiled_result() {
        assertNotSame(new Rexp("\\d"), new Rexp("\\d"));
    }

    @Test
    public void rexp__accepts_options() {
        Matched m;
        m = rexp("[a-z]+").match("<ABC>");
        assertNull(m);
        m = rexp("[a-z]+", "i").match("<ABC>");
        assertNotNull(m);
        assertThat(m.get(0), is("ABC"));
    }

    @Test
    public void rexp__convers_backquote_into_backslash() {
        Matched m = rexp("^`d+$").match("123");
        assertNotNull(m);
        assertThat(m.get(0), is("123"));
    }

    @Test
    public void rexp__accepts_escaping_character() {
        Matched m = rexp("^%d+$", '%').match("123");
        assertNotNull(m);
        assertThat(m.get(0), is("123"));
    }

    @Test
    public void rexp__not_convert_backquote_when_nullchar_passed() {
        Matched m = rexp("^`d+$", '\0').match("123");
        assertNull(m);
    }

    @Test
    public void rexp__returns_MatchedIterator_object_even_when_not_matched() {
        MatchedIterator m = rexp("\\d").matchAll("abc");
        assertNotNull(m);
        assertThat(m, is(MatchedIterator.class));
    }

}
