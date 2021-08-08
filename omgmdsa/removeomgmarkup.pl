#!/usr/bin/env perl


use Getopt::Long ;
use utf8 ;

my ($versionstring)=<<EOF ;
This is removeomgmarkup.pl v0.9
  (c) 2018-2021 Elemental Reasoning, LLC
  (c) 2021 Object Management Group
EOF

sub usage {
  die <<"EOF";
Usage:
        removeomgmarkup.pl FILE.tex > NEWFILE.tex
        removeomgmarkup.pl FILE.tex | followup command

Copyright (C) 2018-2019  Jason McC. Smith (jason@elementalreasoning.com)
EOF
}

my($help,$verbose,$version,$debug);
my($genfiles,$imgfiles,$userfiles);
Getopt::Long::Configure('bundling');
GetOptions('version' => \$version,
           'help|h' => \$help,
           'debug!' => \$debug,
           'verbose!' => \$verbose,
           'base=s' => \$base,
           'genfiles=s' => \$genfiles,
           'userfiles=s' => \$userfiles,
           'imgfiles=s' => \$imgfiles ) or die "Use latexdiff -h to get help.\n" ;

$genfiles = "GeneratedContent/" unless defined($genfiles);
$imgfiles = "Images/" unless defined($imgfiles);
$userfiles = "../" unless defined ($userfiles);
$base = "" unless defined ($base);

if ( $help ) {
  usage() ;
}

if ( $version ) {
  die $versionstring ; 
}

print STDERR $versionstring if $verbose; 

# now we are done setting up and can start working   
my ($file) = @ARGV;
my ($text, $preamble, $body, $post, $output);
my ($encoding);
$encoding="ascii";

if ($file ne '') {
    # check for existence of input files
    if ( ! -e $file ) {
        die "Input file $file does not exist";
    }

    $encoding=guess_encoding($file);

    $encoding = "utf8" if $encoding =~ m/^utf8/i ;
    if (lc($encoding) eq "utf8" ) {
        binmode(STDOUT, ":utf8");
        binmode(STDERR, ":utf8");
    }
    $text=read_file_with_encoding($file,$encoding);
} else {
    $text=do { local $/; <STDIN> };
}

print STDERR $text if $debug;
($preamble,$body,$post)=splitdoc($text,'\\\\begin\{document\}','\\\\end\{document\}');
print STDERR "pre:", $preamble if $debug;
print STDERR "body:", $body if $debug;
print STDERR "post:", $post if $debug;

# $body=replace_genfiles_and_imgfiles_userfiles($body, $genfiles, $imgfiles, $userfiles);
$body=remove_iffileemptyelse($body);
$body=remove_mycomment($body);

# Reconstruct document and print to STDOUT
$output = "";
if ($preamble ne "") {
	$output .= $preamble;
	$output .= '\\begin{document}';
}

$output .= $body;

if ($post ne "") {
	$output .= '\\end{document}' ;
	$output .= $post;
}

print STDOUT $output;



# --------------------


## guess_encoding(filename)
## reads the first 20 lines of filename and looks for call of inputenc package
## if found, return the option of this package (encoding), otherwise return utf8
sub guess_encoding {
  my ($filename)=@_;
  my ($i,$enc);
  $i=0;
  # open (FH, $filename) or die("Couldn't open $filename: $!");
  # while (<FH>) {
  while (<>) {
    next if /^\s*%/;    # skip comment lines
    if (m/\\usepackage\[(\w*?)\]\{inputenc\}/) {
      # close(FH);
      return($1);
    }
    last if (++$i > 20 ); # scan at most 20 non-comment lines
  }
  # close(FH);
  ### return("ascii");
  return("utf8");
}


# ($part1,$part2,$part3)=splitdoc($text,$word1,$word2)
# splits $text into 3 parts at $word1 and $word2.
# if neither $word1 nor $word2 exist, $part1 and $part3 are empty, $part2 is $text
# If only $word1 or $word2 exist but not the other, output an error message.

# NB this version avoids $` and $' for performance reason although it only makes a tiny difference
# (in one test gain a tenth of a second for a 30s run)
sub splitdoc {
  my ($text,$word1,$word2)=@_;
  my ($part1,$part2,$part3)=("","","");
  my ($rest,$pos);

  if ( $text =~ m/(^[^%]*)($word1)/mg ) {
    $pos=pos $text;
    $part1=substr($text,0,$pos-length($2));
    $rest=substr($text,$pos);
    if ( $rest =~ m/(^[^%]*)($word2)/mg ) {
      $pos=pos $rest;
      $part2=substr($rest,0,$pos-length($2));
      $part3=substr($rest,$pos);
    } 
    else {
      die "$word1 and $word2 not in the correct order or not present as a pair." ;
    }
  } else {
    $part2=$text;
    die "$word2 present but not $word1." if ( $text =~ m/(^[^%]*)$word2/ms );
  }
  return ($part1,$part2,$part3);
}

# Has been co-opted by replaceUserFiles.py because I could not figure out
# how to get it to skip the first occurrence in the file, where it is defined.
# i.e. \newcommand{\userfiles}{../} => \newcommand{../}{../} which is an error.
# sub replace_genfiles_and_imgfiles_userfiles {
#   my ($text,$genfiles,$imgfiles,$userfiles)=@_;
#   my ($replacement,$begline,$post);
#   require File::Spec ;
#
#   if ( $text eq "" ) {
#     print STDERR "Empty file\n" if $debug;
#     return ("\n");
#   }
#
#   $text=~s/(^(?:[^%\n]|\\%)*)\\genfiles/{
#     $begfile=(defined($1)? $1 : "") ;
#     "$begfile$genfiles" ;
#     }/exgm;
#
#   $text=~s/(^(?:[^%\n]|\\%)*)\\imgfiles/{
#     $begfile=(defined($1)? $1 : "") ;
#     "$begfile$imgfiles" ;
#     }/exgm;
#
#     $text=~s/(^(?:[^%\n]|\\%)*)\\userfiles/{
#         $begfile=(defined($1)? $1 : "") ;
#         "$begfile$userfiles" ;
#     }/exgm;
#
#   return ($text);
# }


sub remove_iffileemptyelse {
  my ($text)=@_;
  my ($replacement,$begline,$fname);
  require File::Spec ; 

   if ( $text eq "" ) {
       print STDERR "Empty file\n" if $debug;
       return ("\n");
   }
   # If \iffileemptyelse is encountered, mimic the logic - check if exists, check if empty, $3
   # Following balanced parens example from http://perldoc.perl.org/perlre.html
   # (\\iffileemptyelse (\{((?:(?> [^{}]+ ) | (?2) )* ) \} )
   #                    (\{((?:(?> [^{}]+ ) | (?4) )* ) \} )
   #                    (\{((?:(?> [^{}]+ ) | (?6) )* ) \} )
   # )
   # $3, $5, $7 are contents of 1, 2, 3 in command: \iffileemptyelse{1}{2}{3}
   # where 1, 2, and 3 are the filename to check, the if-empty clause, and
   # the if-not-empty clause, respectively.
   # Modify to follow $1 for begline, and they become $4, $6, $8.
   # $text=~s/(^(?:[^%\n]|\\%)*)(\\iffileemptyelse(\{((?:(?> [^{}]+ )|(?3))*)\})(\{((?:(?> [^{}]+ )|(?5))*)\}) (\{((?:(?> [^{}]+ )|(?7))*)\}) )/{
   $text=~s/(^(?:[^%\n]|\\%)*)(\\iffileemptyelse(?:[\s]*)(\{((?:(?>[^{}]+)|(?3))*)\})(?:[\s]*)(\{((?:(?>[^{}]+)|(?5))*)\})(?:[\s]*)(\{((?:(?>[^{}]+)|(?7))*)\}))/{
           if ($debug) {
               print STDERR "FOUND iffileemptyelse: ", $4, "\n";
               print STDERR $1, "\n";
               print STDERR $2, "\n";
               print STDERR $3, "\n";
               print STDERR $4, "\n";
               print STDERR $5, "\n";
               print STDERR $6, "\n";
               print STDERR $7, "\n";
               print STDERR $8, "\n";
           }
           $begline=(defined($1)? $1 : "") ;
           $fname = $4 if defined($4) ;
           $fname .= ".tex" unless $fname =~ m|\.\w{3}$|;
           $fname = $base.$fname;
           $replacement = "";
           if ( -e $fname){
                   if ( -s $fname ) {
                           if ($debug) {
                               print STDERR "File ${fname} exists and is not empty" if $debug;
                               $replacement .= "% File ${fname} exists and is not empty\n";
                           }
                           $replacement .= $8 ;
                   } else {
                           if ($debug) {
                               print STDERR "File ${fname} exists but is empty" if $debug;
                               $replacement .= "% File ${fname} exists but is empty\n";
                           }
                           $replacement .= $6 ;
                   }
           } else {
                   if ($debug) {
                       print STDERR "File ${fname} does not exist" if $debug;
                       $replacement .= "% File ${fname} does not exist\n";
                   }
                   $replacement .= $6 ;
           }
           print STDERR "replacement:", $replacement, "\n" if $debug;
           "$begline$replacement" ;
   }/exgm;
   return($text);
}

sub remove_mycomment {
    my ($text)=@_;
    my ($replacement,$begline);
    require File::Spec ; 

    if ( $text eq "" ) {
        print STDERR "Empty file\n" if $debug;
        return ("\n");
    }
    # \mycomment encountered:
    # \mycomment[author]{text}{comment}
    # Strip out everything but 'text'.
    # Follows example of \iffileemptyeelse above, so text is $6.
    $text=~s/(^(?:[^%\n]|\\%)*)(\\mycomment(?:[\s]*)(\[((?:(?>[^\[\]]+)|(?3))*)\])?(?:[\s]*)(\{((?:(?>[^{}]+)|(?5))*)\})(?:[\s]*)(\{((?:(?>[^{}]+)|(?7))*)\}) )/{
        # print STDERR "FOUND mycomment: ", $8, "\n";
        # print STDERR $1, "\n";
        # print STDERR $2, "\n";
        # print STDERR $3, "\n";
        # print STDERR $4, "\n";
        # print STDERR $5, "\n";
        # print STDERR $6, "\n";
        # print STDERR $7, "\n";
        # print STDERR $8, "\n";
        $begline=(defined($1)? $1 : "") ;
        $replacement = $6;
        # print STDERR "replacement:", $replacement, "\n";
        "$begline$replacement" ;
   }/exgm;

   return($text);
}

sub read_file_with_encoding {
  my ($output);
  my ($filename, $encoding) = @_;

  # print STDERR "encoding: ".$encoding."\n";
  if ($filename eq "") {
          # print STDERR "Reading from STDIN\n";
          local $/ ;
          $output=<STDIN>;
          close STDIN;
          return $output;
  }
  if (lc($encoding) eq "utf8" ) {
    open (FILE, "<:utf8",$filename) or die("Couldn't open $filename: $!");
    local $/ ; # locally set record operator to undefined, ie. enable whole-file mode
    $output=<FILE>;
  } elsif ( lc($encoding) eq "ascii") {
    open (FILE, $filename) or die("Couldn't open $filename: $!");
    local $/ ; # locally set record operator to undefined, ie. enable whole-file mode
    $output=<FILE>;
  } else {
    require Encode;
    open (FILE, "<",$filename) or die("Couldn't open $filename: $!");
    local $/ ; # locally set record operator to undefined, ie. enable whole-file mode
    $output=<FILE>;
    print STDERR "Converting $filename from $encoding to utf8\n" if $verbose;
    $output=Encode::decode($encoding,$output);
  }
  close FILE;
  if ($^O eq "linux" ) {
    $output =~ s/\r\n/\n/g ;
  }
  if (!$output) {
      $output="";
  }
  return $output;
}
