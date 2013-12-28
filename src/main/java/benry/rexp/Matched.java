/**
 *
 */
package benry.rexp;

import java.util.regex.Matcher;
//import java.util.regex.MatchResult;


public class Matched {   // implements MatchResult

    private Matcher _matcher;

    public Matched(Matcher matcher) {
        _matcher = matcher;
    }

    public Matcher getMatcher() { return _matcher; }

    public String get(int n) {
        return _matcher.group(n);
    }

    public int getInt(int n, int whenNull) {
        String s = get(n);
        if (s == null) return whenNull;
        return Integer.parseInt(s);
    }

    public int getInt(int n) {
        String s = get(n);
        return Integer.parseInt(s);
    }

    public int size() {
        return _matcher.groupCount();
    }

    public int start() {
        return _matcher.start();
    }

    public int start(int n) {
        return _matcher.start(n);
    }

    public int end() {
        return _matcher.end();
    }

    public int end(int n) {
        return _matcher.end(n);
    }

}
