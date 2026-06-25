/**
 * Curated external resources surfaced on /learn alongside our content.
 *
 * Source of truth lives in `content/external-resources.yaml`. This file is a
 * static fallback so the UI always has something to render, even before the
 * database has been seeded.
 */
import 'server-only';
import { fetchExternalResources, type ExternalResource } from '@/lib/neon-db';

const STATIC_RESOURCES: Record<string, ExternalResource[]> = {
  math: [
    {
      title: 'Khan Academy — Mathematics',
      url: 'https://www.khanacademy.org/math',
      source: 'Khan Academy',
      language: 'en',
      description:
        'Full curriculum from arithmetic through multivariable calculus and linear algebra.',
    },
    {
      title: 'Khan Academy — מתמטיקה (Hebrew)',
      url: 'https://he.khanacademy.org/math',
      source: 'Khan Academy',
      language: 'he',
      description: 'גרסה עברית מלאה של תוכנית הלימוד במתמטיקה.',
    },
    {
      title: "Paul's Online Math Notes",
      url: 'https://tutorial.math.lamar.edu/',
      source: 'Lamar University',
      language: 'en',
      description: 'Concise notes and worked examples spanning algebra through differential equations.',
    },
    {
      title: 'OpenStax — Pre-Algebra',
      url: 'https://openstax.org/details/books/prealgebra-2e',
      source: 'OpenStax',
      language: 'en',
      description: 'Free, peer-reviewed textbook covering foundational arithmetic and algebra.',
    },
    {
      title: 'Wikipedia — Portal: Mathematics',
      url: 'https://en.wikipedia.org/wiki/Portal:Mathematics',
      source: 'Wikipedia',
      language: 'en',
      description: 'Encyclopedic overview of mathematical topics with rigorous definitions.',
    },
  ],
  physics: [
    {
      title: 'Khan Academy — Physics',
      url: 'https://www.khanacademy.org/science/physics',
      source: 'Khan Academy',
      language: 'en',
      description: 'From kinematics to electromagnetism and modern physics.',
    },
    {
      title: 'Khan Academy — פיזיקה (Hebrew)',
      url: 'https://he.khanacademy.org/science/physics',
      source: 'Khan Academy',
      language: 'he',
      description: 'גרסה עברית של חומרי הלימוד בפיזיקה.',
    },
    {
      title: 'OpenStax — College Physics',
      url: 'https://openstax.org/details/books/college-physics-2e',
      source: 'OpenStax',
      language: 'en',
      description: 'Algebra-based introductory physics textbook with thousands of worked examples.',
    },
    {
      title: 'HyperPhysics',
      url: 'http://hyperphysics.phy-astr.gsu.edu/hbase/hframe.html',
      source: 'Georgia State University',
      language: 'en',
      description: 'Concept map of physics topics with concise, formula-rich explanations.',
    },
    {
      title: 'MIT OpenCourseWare — Classical Mechanics',
      url: 'https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/',
      source: 'MIT OCW',
      language: 'en',
      description: 'Full lecture videos, problem sets, and exams for university-level mechanics.',
    },
  ],
  calculus: [
    {
      title: "Paul's Online Math Notes — Calculus I, II, III",
      url: 'https://tutorial.math.lamar.edu/Classes/CalcI/CalcI.aspx',
      source: 'Lamar University',
      language: 'en',
      description: 'Comprehensive notes and practice problems for single and multivariable calculus.',
    },
    {
      title: 'MIT OpenCourseWare — Single Variable Calculus',
      url: 'https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/',
      source: 'MIT OCW',
      language: 'en',
      description: 'Lectures, problem sets, exams with solutions.',
    },
    {
      title: '3Blue1Brown — Essence of Calculus',
      url: 'https://www.3blue1brown.com/topics/calculus',
      source: '3Blue1Brown',
      language: 'en',
      description: 'Visual, intuition-first video series on calculus.',
    },
    {
      title: 'OpenStax — Calculus Volume 1',
      url: 'https://openstax.org/details/books/calculus-volume-1',
      source: 'OpenStax',
      language: 'en',
      description: 'Free university-level calculus textbook.',
    },
  ],
  linear_algebra: [
    {
      title: '3Blue1Brown — Essence of Linear Algebra',
      url: 'https://www.3blue1brown.com/topics/linear-algebra',
      source: '3Blue1Brown',
      language: 'en',
      description: 'The canonical visual intro to vectors, matrices, eigenvectors.',
    },
    {
      title: 'MIT 18.06 — Linear Algebra (Gilbert Strang)',
      url: 'https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/',
      source: 'MIT OCW',
      language: 'en',
      description: 'Full course by Gilbert Strang with lectures, exams, and solutions.',
    },
  ],
};

export async function getResourcesForSubject(subject: string): Promise<ExternalResource[]> {
  const fromDb = await fetchExternalResources(subject).catch(() => []);
  if (fromDb.length > 0) return fromDb;
  return STATIC_RESOURCES[subject] ?? STATIC_RESOURCES.math ?? [];
}
