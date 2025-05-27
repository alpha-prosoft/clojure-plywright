(ns build
  "Build script for testing.pw library"
  (:require [clojure.tools.build.api :as b]
            [clojure.java.io :as io]))

(def lib (or (System/getenv "CLOJARS_ORG")
             'com.alpha-prosoft/clojure-playwright))
(def version (or (System/getenv "VERSION") "1.0"))
(def class-dir "target/classes")
(def basis (b/create-basis {:project "deps.edn"}))
(def jar-file (format "target/%s-%s.jar" (name lib) version))
(def pom-file "target/classes/META-INF/maven/com.alpha-prosoft/clojure-playwright/pom.xml")

(defn clean [_]
  (b/delete {:path "target"}))

(defn jar [_]
  (println "Building JAR for" lib "version" version)
  (clean nil)
  (b/write-pom {:class-dir class-dir
                :lib lib
                :version version
                :basis basis
                :src-dirs ["src"]
                :scm {:url "https://github.com/alpha-prosoft/clojure-playwright"
                      :connection "scm:git:git://github.com/alpha-prosoft/clojure-playwright.git"
                      :developerConnection "scm:git:ssh://git@github.com/alpha-prosoft/clojure-playwright.git"
                      :tag (str "v" version)}
                 :pom-data [[:description "Playwright-native testing library for Clojure — browser automation with Trace Viewer reporting"]
                           [:url "https://github.com/alpha-prosoft/clojure-playwright"]
                           [:licenses
                            [:license
                             [:name "Eclipse Public License 2.0"]
                             [:url "https://www.eclipse.org/legal/epl-2.0/"]]]
                           [:developers
                            [:developer
                             [:name "Alpha Prosoft"]
                             [:email "info@alpha-prosoft.com"]]]]})
  
  ;; Copy pom.xml to project root for deps-deploy
  (io/copy (io/file pom-file) (io/file "pom.xml"))
  (println "POM file copied to project root: pom.xml")
  
  (b/copy-dir {:src-dirs ["src" "resources"]
               :target-dir class-dir})
  
  (b/jar {:class-dir class-dir
          :jar-file jar-file})
  
  (println "JAR created:" jar-file))

(defn deploy [_]
  (println "Deploying" lib "version" version "to Clojars")
  (println "Note: Deploy function should be called via deps-deploy")
  (println "Run: clojure -X:deploy :artifact" jar-file))

(defn install [_]
  (println "Installing" lib "version" version "to local Maven repository")
  (jar nil)
  (b/install {:basis basis
              :lib lib
              :version version
              :jar-file jar-file
              :class-dir class-dir})
  (println "Successfully installed" lib version "locally"))
