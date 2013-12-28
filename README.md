benry.java
==========

Useful tools for java.

$License: MIT License $


## Package: bency.rexp

Useful wrapper over `java.util.regex` package.


### Matching

	import static benry.rexp.Rexp.rexp;
	import benry.rexp.Matched;
	
	public class Example {
	    public static void main(String args[]) {
	
	        // once
	        Matched m = rexp("^(\\d+)-(\\d+)-(\\d+)$").match("2000-12-31");
	        if (m != null) {
	            System.out.println(m.get(0));  //=> 2000-12-31
	            System.out.println(m.get(1));  //=> 2000
	            System.out.println(m.get(2));  //=> 12
	            System.out.println(m.get(3));  //=> 31
	            //
	            System.out.println(m.size());  //=> 3
	            //
	            System.out.println(m.start(1));  //=> 0
	            System.out.println(m.start(2));  //=> 5
	            System.out.println(m.start(3));  //=> 8
	            System.out.println(m.end(1));    //=> 4
	            System.out.println(m.end(2));    //=> 7
	            System.out.println(m.end(3));    //=> 10
	        }
	
	        // all
	        for (Matched m2: rexp("(\\d+)").matchAll("2000-12-31")) {
	            System.out.println(m2.get(1));  //=> 2000
	                                            //=> 12
	                                            //=> 31
	        }
	
	    }
	}


### Replacing

	import benry.rexp.Matched;
	import benry.rexp.Replacer;
	
	public class Example {
	    public static void main(String args[]) {
	
	        // replaces all
	        String result;
	        result = rexp("\\d+").gsub("2000-12-31", "X");
	        System.out.println(result);      //=> X-X-X
	        result = rexp("(\\d+)").gsub("2000-12-31", "<$1>");
	        System.out.println(result);      //=> <2000>-<12>-<31>
	
	        // replaces first
	        result = rexp("\\d+").sub("2000-12-31", "X");
	        System.out.println(result);      //=> X-12-31
	        result = rexp("(\\d+)").sub("2000-12-31", "<$1>");
	        System.out.println(result);      //=> <2000>-12-31
	
	        // replaces with callback
	        result = rexp("(\\d+)").gsub("2000-12-31", new Replacer() {
	            public String replace(Matched m) {
	                int intval = Integer.parseInt(m.get(1));
	                return Integer.toString(intval + 1);
	            }
	        });
	        System.out.println(result);      //=> 2001-13-32
	        result = rexp("(\\d+)").sub("2000-12-31", new Replacer() {
	            public String replace(Matched m) {
	                int intval = Integer.parseInt(m.get(1));
	                return Integer.toString(intval + 1);
	            }
	        });
	        System.out.println(result);      //=> 2001-12-31
	
	    }
	}


### Splitting

	import static benry.rexp.Rexp.rexp;
	import benry.rexp.Matched;
	
	public class Example {
	    public static void main(String args[]) {
	
	        String[] items = rexp("\\s+").split("Haruhi  Mikuru   Yuki");
	        System.out.println(items.length);  //=> 3
	        for (String item: items) {
	            System.out.println(item);    //=> Haruhi
	                                         //=> Mikuru
	                                         //=> Yuki
	        }
	
	    }
	}


### Pattern Options

	import static benry.rexp.Rexp.rexp;
	import benry.rexp.Matched;
	
	public class Example {
	    public static void main(String args[]) {
	
	        // case-sensitive and insensitive matching
	        Matched m1 = rexp("[a-z]+").match("SOS");
	        System.out.println(m1);         //=> null
	        Matched m2 = rexp("[a-z]+", "i").match("SOS");
	        System.out.println(m2.get(0));  //=> SOS
	
	    }
	}

For example, `"ims"` means `Pattern.CASE_INSENSITIVE | Pattern.MULTILINE | Pattern.DOTALL`.

* "i" : Pattern.CASE_INSENSITIVE
* "m" : Pattern.MULTILINE
* "s" : Pattern.DOTALL
* "x" : Pattern.COMMENTS
* "u" : Pattern.UNICODE_EQ
* "d" : Pattern.UNIX_LINES
* "E" : Pattern.CANON_EQ
* "L" : Pattern.LITERAL


### Avoid Backslash-Hell

	import static benry.rexp.Rexp.rexp;
	import benry.rexp.Matched;
	
	public class Example {
	    public static void main(String args[]) {
	
	        // use backquote instead of backslash
	        Matched m1 = rexp("^(`d`d)/(`d`d)$").match("12/31");
	        System.out.println(m1.get(1));    //=> 12
	        System.out.println(m1.get(2));    //=> 31
	
	        // use arbitrary character instead of backslash
	        Matched m2 = rexp("^(%d%d)/(%d%d)$", '%').match("12/31");
	        System.out.println(m2.get(1));    //=> 12
	        System.out.println(m2.get(2));    //=> 31
	
	        // disable backquote
	        Matched m3 = rexp("^(`d`d)/(`d`d)$", '\0').match("12/31");
	        System.out.println(m3);           //=> null
	
	    }
	}


### Caching Compiled Pattern

`rexp()` caches compiled pattern object into memory.

	// pattern is compiled only once, because rexp() caches
	// compiled pattern object into memory.
	for (String filename: filenames) {
	    if (rexp("\\.(jpg|png|gif)$").match(filename) != null) {
	        System.out.println(filename + ": image file");
	    }
	}

If there is no need to cache pattern into memory, use `new Rexp()` instead of `rexp()`.

	import benry.rexp.Rexp;
	class Example {
	    // use new Rexp because there is no need to cache pattern
	    static Rexp SUFFIX_REXP = new Rexp("\\.(jpg|png|gif)$");
	}
