/**
 * $License: MIT License $
 */
package benry.rexp;

import java.util.Iterator;


public class MatchedIterator implements Iterable<Matched>, Iterator<Matched> {

    private Matched _matched;

    MatchedIterator(Matched matched) {
        _matched = matched;
    }

    public Iterator<Matched> iterator() {
        return this;
    }

    public boolean hasNext() {
        return _matched.getMatcher().find();
    }

    public Matched next() {
        return _matched;
    }

    public void remove() {
        throw new UnsupportedOperationException();
    }

}