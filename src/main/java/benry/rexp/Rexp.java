/**
 * $License: MIT License $
 */
package benry.rexp;

import java.util.HashMap;
import java.util.regex.Pattern;
import java.util.regex.Matcher;


public class Rexp {

    private Pattern _pattern;

    public Rexp(String pattern) {
        this(pattern, null, '`');
    }

    public Rexp(String pattern, String flags) {
        this(pattern, flags, '`');
    }

    public Rexp(String pattern, char escapeChar) {
        this(pattern, null, escapeChar);
    }

    public Rexp(String pattern, String flags, char escapeChar) {
        if (escapeChar != '\0') {
            pattern = pattern.replace(escapeChar, '\\');
        }
        _pattern = Pattern.compile(pattern, toIntFlag(flags));
    }

    public Pattern getPattern() { return _pattern; }

    public Matched match(CharSequence input) {
        Matcher m = _pattern.matcher(input);
        return m.find() ? new Matched(m) : null;
    }

    public MatchedIterator matchAll(CharSequence input) {
        return new MatchedIterator(new Matched(_pattern.matcher(input)));
    }

    public String gsub(String input, String replacement) {
        return _pattern.matcher(input).replaceAll(replacement);
    }

    public String gsub(String input, Replacer replacer) {
        return sub(input, replacer, -1);
    }

    public String sub(String input, String replacement) {
        return _pattern.matcher(input).replaceFirst(replacement);
    }

    public String sub(String input, Replacer replacer) {
        return sub(input, replacer, 1);
    }

    public String sub(String input, Replacer replacer, int times) {
        if (times == 0) return input;
        StringBuilder sb = new StringBuilder();
        int pos = 0;
        for (Matched m: matchAll(input)) {
            sb.append(input.subSequence(pos, m.start()));
            sb.append(replacer.replace(m));
            pos = m.end();
            times--;
            if (times == 0) break;
        }
        if (pos == 0) return input;
        sb.append(input.subSequence(pos, input.length()));
        return sb.toString();
    }

    public String[] split(CharSequence input) {
        return _pattern.split(input, 0);
    }

    public String[] split(CharSequence input, int limit) {
        if (limit == 0) return new String[]{input.toString()};
        return _pattern.split(input, limit);
    }

    static int toIntFlag(String flags) {
        int intflag = 0x0;
        if (flags == null) return intflag;
        for (int i = 0, len = flags.length(); i < len; i++) {
            char c = flags.charAt(i);
            if      (c == 'i') intflag |= Pattern.CASE_INSENSITIVE;
            else if (c == 'm') intflag |= Pattern.MULTILINE;
            else if (c == 's') intflag |= Pattern.DOTALL;
            else if (c == 'x') intflag |= Pattern.COMMENTS;
            else if (c == 'u') intflag |= Pattern.UNICODE_CASE;
            else if (c == 'd') intflag |= Pattern.UNIX_LINES;
            else if (c == 'E') intflag |= Pattern.CANON_EQ;
            else if (c == 'L') intflag |= Pattern.LITERAL;
            else {
                throw new UnknownPatternFlagError("'"+c+"': unknown pattern flag.");
            }
        }
        return intflag;
    }

    static HashMap<Object, Rexp> _cache = new HashMap<Object, Rexp>();

    public static Rexp rexp(String pattern, String flags, char escapeChar) {
        Object key = flags == null && escapeChar == '`'
                   ? pattern
                   : new String[] {pattern, flags, Character.toString(escapeChar)};
        Rexp rexp = _cache.get(key);
        if (rexp == null) {
            rexp = new Rexp(pattern, flags, escapeChar);
            _cache.put(key, rexp);
        }
        return rexp;
    }

    public static Rexp rexp(String pattern) {
        return rexp(pattern, null, '`');
    }

    public static Rexp rexp(String pattern, String flags) {
        return rexp(pattern, flags, '`');
    }

    public static Rexp rexp(String pattern, char escapeChar) {
        return rexp(pattern, null, escapeChar);
    }

}
